import unittest
from pathlib import Path


class ViewerImageReferenceShellSmokeTestCase(unittest.TestCase):
    def test_reference_image_input_hooks_exist(self) -> None:
        html_path = Path("frontend/index.html")
        main_js_path = Path("frontend/js/viewer/main.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(main_js_path.exists())

        html = html_path.read_text(encoding="utf-8")
        main_js = main_js_path.read_text(encoding="utf-8")

        self.assertIn('id="reference-image-url"', html)
        self.assertIn("reference-image-url", main_js)
        self.assertIn("reference_image_url", main_js)


if __name__ == "__main__":
    unittest.main()
