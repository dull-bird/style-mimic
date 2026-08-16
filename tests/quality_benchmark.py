#!/usr/bin/env python3
"""Small, reproducible quality gate over bundled samples and controls.

This is deliberately not a detector benchmark: there is no gold label saying
that a text was written by a person or a model.  It checks invariants that the
review tool must satisfy (safe empty/short input, controlled discrimination,
and symmetric similarity) and records metrics for the bundled samples.
"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_analyze  # noqa: E402
import style_review  # noqa: E402


def _file(text):
    f = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False)
    f.write(text)
    f.close()
    return pathlib.Path(f.name)


def _score(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args)


def main():
    samples = {
        "oakley": (ROOT / "examples/style-paper/samples/oakley.txt", "en"),
        "luxun": (ROOT / "examples/style-paper/samples/luxun.txt", "zh"),
        "qianzhongshu": (ROOT / "examples/style-paper/samples/qianzhongshu.txt", "zh"),
        "tongcheng": (ROOT / "examples/style-paper/samples/tongcheng.txt", "zh"),
        "trump": (ROOT / "examples/style-paper/samples/trump.txt", "en"),
    }
    metrics = {}
    for name, (path, expected_lang) in samples.items():
        if not path.exists():
            continue  # Bundled author corpora are optional examples.
        result = style_analyze.analyze(str(path))
        assert result["lang"] == expected_lang, (name, result["lang"])
        assert result["units"] > 1000, (name, result["units"])
        assert result["tail"]["reliable"], name
        metrics[name] = {
            "lang": result["lang"],
            "units": result["units"],
            "sentences": result["sentences"],
            "cv": result["tail"]["cv"],
            "p05": result["tail"]["p05"],
            "p95": result["tail"]["p95"],
        }

    plain = _file("We test one idea. We record the result. We change one variable. " * 20)
    ai = _file(
        "In today's rapidly evolving world, it is important to note that this pivotal framework fosters a vibrant tapestry. "
        "In conclusion, it serves as a testament to progress. " * 20
    )
    unrelated = _file("Quantum fields drift across the silent valley. Marble engines measure distant stars. " * 30)
    same = _file("We test one idea. We record the result. We change one variable. " * 20)
    paraphrase = _file("We test one idea. We log the result. We change one variable. " * 20)
    try:
        plain_score = _score(style_review.aiflavor, str(plain))
        ai_score = _score(style_review.aiflavor, str(ai))
        same_score = _score(style_review.sim, str(plain), str(same))
        paraphrase_score = _score(style_review.sim, str(plain), str(paraphrase))
        unrelated_score = _score(style_review.sim, str(plain), str(unrelated))
        assert ai_score > plain_score, (ai_score, plain_score)
        assert plain_score <= 10, plain_score
        assert same_score == 100, same_score
        assert paraphrase_score >= 85, paraphrase_score
        assert unrelated_score < 85, unrelated_score
        metrics["controls"] = {
            "plain_ai_flavor": plain_score,
            "clustered_ai_flavor": ai_score,
            "same_text_similarity": same_score,
            "same_voice_paraphrase_similarity": paraphrase_score,
            "disjoint_vocab_similarity": unrelated_score,
        }
    finally:
        for path in (plain, ai, unrelated, same, paraphrase):
            path.unlink(missing_ok=True)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
