#!/usr/bin/env python3
"""Generate the voice appendix from the shared JSON source."""
from __future__ import annotations

import argparse
import json
import pathlib


SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def latex_escape(value: str) -> str:
    return "".join(SPECIALS.get(char, char) for char in str(value))


def make_voice_box(voice: dict, units: dict[str, str], index: int) -> str:
    lines = [
        r"\begin{voicebox}",
        rf"\textbf{{{index:02d} / {latex_escape(voice['name'])}}}\\",
        rf"\textsc{{{latex_escape(voice['language'])} · {latex_escape(voice['era'])} · {latex_escape(voice['register'])}}}",
        rf"\emph{{{latex_escape(voice['disclaimer'])}}}",
    ]
    for key, label in units.items():
        lines.extend([
            rf"\subsection*{{{latex_escape(label)}}}",
            latex_escape(voice["sections"][key]),
        ])
    lines.append(r"\end{voicebox}")
    return "\n\n".join(lines)


def make_metrics_table(data: dict) -> str:
    rows = [
        "% Generated from data/styles.json; values are review signals.",
        r"\begin{longtable}{@{}lllll@{}}",
        r"\toprule Voice & Language & CV & AI flavor & Similarity \\",
        r"\midrule",
    ]
    for voice in data["voices"]:
        metrics = voice.get("metrics", {})
        values = [
            voice["name"],
            voice["language"],
            metrics.get("cv", "--"),
            metrics.get("ai_flavor", "--"),
            metrics.get("similarity", "--"),
        ]
        rows.append(" & ".join(latex_escape(str(value)) for value in values) + r" \\")
    rows.extend([r"\bottomrule", r"\end{longtable}"])
    return "\n".join(rows) + "\n"


def generate(data_path: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / "generated-voices.tex"
    chunks = [
        "% Generated from data/styles.json; do not edit manually.",
        rf"\section{{{latex_escape(data['title'])}}}",
        latex_escape(data["ethics"]),
    ]
    for index, voice in enumerate(data["voices"], start=1):
        chunks.append(rf"\section{{{latex_escape(voice['name'])}}}")
        chunks.append(make_voice_box(voice, data["units"], index))
    output.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
    (out_dir / "metrics-table.tex").write_text(make_metrics_table(data), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    print(generate(args.data, args.out))


if __name__ == "__main__":
    main()
