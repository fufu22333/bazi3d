import unittest
from pathlib import Path


class ViewerAnimationShellSmokeTestCase(unittest.TestCase):
    def test_animation_hooks_exist_without_replacing_viewer_structure(self) -> None:
        html_path = Path("frontend/index.html")
        main_js_path = Path("frontend/js/viewer/main.js")
        animation_js_path = Path("frontend/js/viewer/animation.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(main_js_path.exists())
        self.assertTrue(animation_js_path.exists())

        html = html_path.read_text(encoding="utf-8")
        main_js = main_js_path.read_text(encoding="utf-8")
        animation_js = animation_js_path.read_text(encoding="utf-8")

        self.assertIn('id="play-idle"', html)
        self.assertIn('id="play-wave"', html)
        self.assertIn('id="motion-status"', html)

        self.assertIn("createAnimationLayer", animation_js)
        self.assertIn("hasModel", animation_js)
        self.assertIn("playClip", animation_js)

        self.assertIn("createAnimationLayer", main_js)
        self.assertIn("play-idle", main_js)
        self.assertIn("play-wave", main_js)


if __name__ == "__main__":
    unittest.main()
