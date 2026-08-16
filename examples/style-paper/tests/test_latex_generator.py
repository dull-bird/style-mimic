#!/usr/bin/env python3
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_latex.py"
DATA = ROOT / "data" / "styles.json"
sys.path.insert(0, str(ROOT / "scripts"))
from generate_latex import latex_escape  # noqa: E402


class LatexGeneratorTests(unittest.TestCase):
    def test_generator_emits_all_voice_ids_and_escapes_latex(self):
        with tempfile.TemporaryDirectory() as temp:
            out_dir = pathlib.Path(temp)
            subprocess.run(
                [sys.executable, str(GENERATOR), "--data", str(DATA), "--out", str(out_dir)],
                check=True,
                text=True,
            )
            generated = (out_dir / "generated-voices.tex").read_text(encoding="utf-8")
            self.assertIn(r"\section{苏轼", generated)
            self.assertIn("Barbara Oakley", generated)
            self.assertEqual(latex_escape("A&B"), r"A\&B")
            self.assertNotIn("style-mimic &", generated)

    def test_generated_metadata_matches_json_voice_count(self):
        with tempfile.TemporaryDirectory() as temp:
            out_dir = pathlib.Path(temp)
            subprocess.run(
                [sys.executable, str(GENERATOR), "--data", str(DATA), "--out", str(out_dir)],
                check=True,
            )
            data = json.loads(DATA.read_text(encoding="utf-8"))
            generated = (out_dir / "generated-voices.tex").read_text(encoding="utf-8")
            self.assertEqual(generated.count(r"\begin{voicebox}"), len(data["voices"]))


if __name__ == "__main__":
    unittest.main()
