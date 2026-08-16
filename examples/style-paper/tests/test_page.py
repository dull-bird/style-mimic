#!/usr/bin/env python3
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class StaticPageTests(unittest.TestCase):
    def test_page_has_required_mounts_and_local_assets(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="voice-grid"', html)
        self.assertIn('id="section-tabs"', html)
        self.assertIn('src="app.js"', html)
        self.assertIn('href="styles.css"', html)

    def test_page_does_not_reference_external_assets(self):
        for name in ("index.html", "styles.css", "app.js"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("https://", text)
            self.assertNotIn("http://", text)


if __name__ == "__main__":
    unittest.main()
