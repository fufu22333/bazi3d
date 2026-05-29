import unittest
from pathlib import Path


class GalleryShellSmokeTestCase(unittest.TestCase):
    def test_gallery_page_hooks_exist(self) -> None:
        html_path = Path("frontend/gallery.html")
        script_path = Path("frontend/js/gallery.js")
        api_path = Path("frontend/js/api.js")
        viewer_path = Path("frontend/js/viewer/main.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(script_path.exists())
        self.assertTrue(api_path.exists())
        self.assertTrue(viewer_path.exists())

        html = html_path.read_text(encoding="utf-8")
        script = script_path.read_text(encoding="utf-8")
        api_script = api_path.read_text(encoding="utf-8")
        viewer_script = viewer_path.read_text(encoding="utf-8")

        self.assertIn('id="gallery-list"', html)
        self.assertIn('id="gallery-status"', html)
        self.assertIn('class="gallery-grid"', html)
        self.assertIn("作品广场", html)
        self.assertIn("公开作品集", html)
        self.assertIn("fetchWorks", api_script)
        self.assertIn("renderWorks", script)
        self.assertIn("gallery-grid", script)
        self.assertIn("viewer.html?", script)
        self.assertIn('autoload: "1"', script)
        self.assertIn("URLSearchParams", viewer_script)
        self.assertNotIn("毕业论文", script)


if __name__ == "__main__":
    unittest.main()
