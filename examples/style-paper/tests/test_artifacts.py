#!/usr/bin/env python3
import json
import pathlib
import shutil
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "styles.json"
PDF = ROOT / "tex" / "style-mimic-paper.pdf"
sys.path.insert(0, str(ROOT / "scripts"))
from measure_styles import measure  # noqa: E402


class DeliveredArtifactTests(unittest.TestCase):
    def test_every_voice_has_reproducible_review_metrics(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(len(data["voices"]), 11)
        required = {"cv", "p05", "p95", "iqr", "mattr", "ai_flavor", "similarity"}
        for voice in data["voices"]:
            self.assertTrue(required.issubset(voice.get("metrics", {})), voice["id"])
            self.assertGreaterEqual(voice["metrics"]["ai_flavor"], 0)
            self.assertLessEqual(voice["metrics"]["ai_flavor"], 100)
            self.assertGreaterEqual(voice["metrics"]["similarity"], 0)
            self.assertLessEqual(voice["metrics"]["similarity"], 100)

    def test_pdf_and_generated_appendix_exist(self):
        self.assertGreater(PDF.stat().st_size, 10_000)
        generated = (ROOT / "tex" / "generated-voices.tex").read_text(encoding="utf-8")
        metrics = (ROOT / "tex" / "metrics-table.tex").read_text(encoding="utf-8")
        self.assertEqual(generated.count(r"\begin{voicebox}"), 11)
        self.assertEqual(metrics.count(r"\\"), 12)  # header + 11 voices

    def test_measure_script_populates_a_clean_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "styles.json"
            shutil.copyfile(DATA, target)
            result = measure(target)
            self.assertEqual(len(result["voices"]), 11)
            measured = json.loads(target.read_text(encoding="utf-8"))
            self.assertTrue(all("similarity" in voice["metrics"] for voice in measured["voices"]))


if __name__ == "__main__":
    unittest.main()
