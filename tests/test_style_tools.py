#!/usr/bin/env python3
"""Behavioral regression tests for the zero-dependency style tools.

These tests intentionally use short, synthetic texts so they can run in CI
without downloading a corpus or a tokenizer.  The larger benchmark in
``tests/quality_benchmark.py`` exercises the bundled author samples.
"""
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import style_analyze  # noqa: E402
import style_review  # noqa: E402


class TextFixture(unittest.TestCase):
    def write_text(self, text, suffix=".txt"):
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=suffix, delete=False
        )
        handle.write(text)
        handle.close()
        self.addCleanup(pathlib.Path(handle.name).unlink, missing_ok=True)
        return handle.name


class LanguageAndCountingTests(TextFixture):
    def test_short_chinese_is_detected_as_chinese(self):
        path = self.write_text("学习。")
        result = style_analyze.analyze(path)
        self.assertEqual(result["lang"], "zh")
        self.assertEqual(result["units"], 2)
        self.assertEqual(result["sentences"], 1)

    def test_chinese_pronoun_vector_does_not_double_count_plural_forms(self):
        result = style_analyze.pronoun_vector("我 我们 你 你们 他 他们", "zh")
        self.assertEqual(result, {"1sg": 111.1, "1pl": 111.1,
                                  "2nd": 222.2, "3rd": 222.2})

    def test_english_sentence_and_word_counts_are_stable(self):
        path = self.write_text("One short sentence. A second sentence follows.")
        result = style_analyze.analyze(path)
        self.assertEqual(result["lang"], "en")
        self.assertEqual(result["units"], 7)
        self.assertEqual(result["sentences"], 2)

    def test_chinese_markers_are_longest_first_and_tan_is_not_a_clause(self):
        counts = style_analyze.marker_counts("但是但我们", "zh")
        self.assertEqual(counts["adversative"], 2)
        self.assertEqual(counts["self"], 1)
        self.assertEqual(style_analyze.clauses_per_sentence(["苹果、香蕉、梨。"], "zh"), [1])

    def test_chinese_metrics_have_a_standard_library_fallback(self):
        old = style_analyze.jieba
        style_analyze.jieba = None
        self.addCleanup(setattr, style_analyze, "jieba", old)
        self.assertEqual(style_analyze.zh_tokens("学习方法"), list("学习方法"))


class TailStatisticsTests(TextFixture):
    def test_sentence_length_report_exposes_robust_tail_statistics(self):
        text = " ".join(["短句。"] * 8 + ["这是一个明显更长的句子，用来检验长尾统计是否保留。"] * 2)
        result = style_analyze.analyze(self.write_text(text))
        lengths = result["sent_len"]
        for key in ("p05", "p95", "iqr", "mad", "skewness", "cv"):
            self.assertIn(key, lengths)
        self.assertGreaterEqual(lengths["p95"], lengths["p05"])
        self.assertGreater(lengths["p95"], lengths["p50"] if "p50" in lengths else lengths["median"])


class ReviewBehaviorTests(TextFixture):
    def test_aiflavor_is_low_for_plain_text_and_high_for_clustered_patterns(self):
        plain = " ".join(["我们先看一个具体例子。这个方法有两个步骤。"] * 20)
        ai = " ".join([
            "在当今时代，学习能力的提升显得尤为重要。",
            "研究表明，这一方法能够赋能学习者，构建知识闭环。",
            "总而言之，让我们共同开启人生的新篇章。",
        ] * 20)
        plain_out = io.StringIO()
        ai_out = io.StringIO()
        with contextlib.redirect_stdout(plain_out):
            plain_score = style_review.aiflavor(self.write_text(plain))
        with contextlib.redirect_stdout(ai_out):
            ai_score = style_review.aiflavor(self.write_text(ai))
        self.assertLess(plain_score, ai_score)
        self.assertIn("模式", ai_out.getvalue())

    def test_uniform_but_plain_sentences_do_not_trigger_variance_penalty(self):
        plain = " ".join(["We test one idea."] * 30)
        with contextlib.redirect_stdout(io.StringIO()):
            score = style_review.aiflavor(self.write_text(plain))
        self.assertLessEqual(score, 10)

    def test_variance_penalty_report_has_complete_evidence_columns(self):
        # Four nearby lengths keep CV low while satisfying the anti-subtitle
        # gate that requires genuine length variation.
        sentences = []
        for i in range(8):
            sentences.extend([
                "We test one small idea today.",
                "We test one small idea today again.",
                "We test one small idea today again now.",
                "We test one small idea today again now together.",
            ])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            score = style_review.aiflavor(self.write_text(" ".join(sentences)))
        self.assertGreater(score, 0)
        self.assertRegex(output.getvalue(), "方差塌缩|节奏偏匀")
        self.assertIn("句长分布", output.getvalue())

    def test_empty_input_is_safe_and_reports_low_confidence(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            score = style_review.aiflavor(self.write_text(""))
        self.assertEqual(score, 0)
        self.assertIn("样本过短", output.getvalue())

    def test_similarity_is_symmetric_and_identical_text_is_perfect(self):
        a = self.write_text("我们先看例子。这个方法有两个步骤。然后再检查结果。" * 8)
        b = self.write_text("我们先看例子。这个方法有两个步骤。然后再检查结果。" * 8)
        with contextlib.redirect_stdout(io.StringIO()):
            ab = style_review.sim(a, b)
            ba = style_review.sim(b, a)
            aa = style_review.sim(a, a)
        self.assertEqual(aa, 100)
        self.assertEqual(ab, ba)

    def test_similarity_warns_when_inputs_are_too_small_for_a_style_claim(self):
        a = self.write_text("短句。")
        b = self.write_text("另一句。")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            style_review.sim(a, b)
        self.assertIn("样本过短", output.getvalue())

    def test_equal_length_but_disjoint_vocabularies_are_not_same_voice(self):
        a = self.write_text("We test one idea. We record the result. " * 20)
        b = self.write_text("Quantum fields drift. Marble engines turn. " * 20)
        with contextlib.redirect_stdout(io.StringIO()):
            score = style_review.sim(a, b)
        self.assertLess(score, 85)


if __name__ == "__main__":
    unittest.main()
