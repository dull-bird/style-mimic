#!/usr/bin/env python3
"""Measure every showcase voice against a neutral same-language baseline.

The page and LaTeX appendix share ``styles.json``.  This script keeps their
numbers reproducible by calling the repository's own ``style_analyze`` and
``style_review`` implementations rather than reimplementing metrics here.
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile


HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from style_analyze import analyze  # noqa: E402
from style_review import aiflavor, sim  # noqa: E402


BASELINES = {
    "中文": (
        "本文讨论一个文风分析框架。框架把同一论点放进固定的语义骨架，"
        "再分别观察词汇、句法、衔接、修辞、立场和叙事声音。研究者先建立"
        "平均作者基线，再记录目标文本与基线之间的差异。\n\n"
        "分析报告同时保留均值和尾部，包含中位数、分位数、四分位距、"
        "中位绝对偏差、偏度与变异系数。少量样本只能提供线索，不能支撑"
        "稳定的身份判断。review 工具应列出命中的模式与原文证据，写作者"
        "据此修改，再用人工朗读和同伴评阅确认结果。"
    ),
    "English": (
        "This paper describes a small framework for measuring writing style. "
        "It keeps the semantic skeleton fixed and observes vocabulary, syntax, "
        "cohesion, rhetoric, stance, and narrative voice as separate signals. "
        "A neutral baseline is built before the target text is described as a "
        "difference from that baseline.\n\n"
        "The report keeps both averages and tails: medians, percentiles, spread, "
        "skewness, and the coefficient of variation. Short samples are clues, "
        "not stable identity evidence. A review should show each pattern and its "
        "source span, after which a writer revises the draft and reads it aloud."
    ),
}


def voice_text(voice: dict) -> str:
    return "\n\n".join(voice["sections"].values())


def measure(data_path: pathlib.Path) -> dict:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="style-paper-metrics-") as temp:
        tmp = pathlib.Path(temp)
        baseline_paths = {}
        for language, text in BASELINES.items():
            path = tmp / f"baseline-{language}.txt"
            path.write_text(text, encoding="utf-8")
            baseline_paths[language] = path

        rows = []
        for voice in data["voices"]:
            path = tmp / f"{voice['id']}.txt"
            path.write_text(voice_text(voice), encoding="utf-8")
            result = analyze(str(path))
            # The review functions intentionally print human-readable reports;
            # capture them here so this batch command emits one compact table.
            with contextlib.redirect_stdout(io.StringIO()):
                ai_score = aiflavor(str(path))
                similarity = sim(str(baseline_paths[voice["language"]]), str(path))
            voice["metrics"] = {
                "cv": result["tail"]["cv"],
                "p05": result["tail"]["p05"],
                "p95": result["tail"]["p95"],
                "iqr": result["tail"]["iqr"],
                "mattr": result["mattr"],
                "ai_flavor": ai_score,
                "similarity": similarity,
                "sentences": result["sentences"],
                "units": result["units"],
                "tail_reliable": result["tail"]["reliable"],
            }
            rows.append((voice["name"], voice["language"], voice["metrics"]))

    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"voices": rows, "data": data_path}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: measure_styles.py path/to/styles.json")
    result = measure(pathlib.Path(sys.argv[1]).resolve())
    print("voice\tlanguage\tCV\tAI flavor\tsimilarity\ttail reliable")
    for name, language, metrics in result["voices"]:
        print(
            f"{name}\t{language}\t{metrics['cv']}\t{metrics['ai_flavor']}"
            f"\t{metrics['similarity']}\t{metrics['tail_reliable']}"
        )


if __name__ == "__main__":
    main()
