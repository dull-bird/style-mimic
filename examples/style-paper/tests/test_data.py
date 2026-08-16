#!/usr/bin/env python3
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "styles.json"


class DataContractTests(unittest.TestCase):
    def test_dataset_has_eleven_voices_and_five_shared_sections(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(len(data["voices"]), 11)
        expected = {"abstract", "method", "case", "limits", "conclusion"}
        self.assertEqual(set(data["units"]), expected)
        self.assertEqual({"abstract", "method", "case", "limits", "conclusion"}, expected)
        self.assertEqual(len({voice["id"] for voice in data["voices"]}), 11)
        for voice in data["voices"]:
            self.assertEqual(set(voice["sections"]), expected)
            self.assertTrue(all(voice["sections"][key].strip() for key in expected))
            self.assertTrue(voice["disclaimer"].strip())

    def test_dataset_has_ethics_and_canonical_thesis(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertIn("ethics", data)
        self.assertIn("thesis", data)
        self.assertGreater(len(data["thesis"]), 40)


if __name__ == "__main__":
    unittest.main()
