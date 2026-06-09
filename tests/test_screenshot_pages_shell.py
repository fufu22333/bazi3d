import unittest
from pathlib import Path


class ScreenshotPagesShellTestCase(unittest.TestCase):
    def test_separated_screenshot_pages_exist_with_distinct_hooks(self) -> None:
        pages = {
            "create.html": (
                'id="screenshot-create-page"',
                'id="rule-input-form"',
                "./js/create-page.js",
                "生日礼物模型定制",
                'id="occasion"',
                'id="relationship"',
                'id="gift-message"',
                'id="favorite-color"',
            ),
            "task.html": (
                'id="screenshot-task-page"',
                'id="task-timeline"',
                "./js/task-page.js",
                "礼物模型生成进度",
            ),
            "viewer.html": (
                'id="screenshot-viewer-page"',
                'id="viewer-canvas"',
                "./js/viewer-page.js",
                "3D",
            ),
        }

        for filename, expected_fragments in pages.items():
            with self.subTest(filename=filename):
                html = Path("frontend", filename).read_text(encoding="utf-8")
                self.assertIn("data-nav-root", html)
                self.assertIn('data-nav-link="home"', html)
                self.assertIn('data-nav-link="gallery"', html)
                self.assertIn('data-nav-link="profile"', html)
                for fragment in expected_fragments:
                    self.assertIn(fragment, html)

    def test_screenshot_page_scripts_exist_and_use_existing_api_boundaries(self) -> None:
        create_script = Path("frontend/js/create-page.js").read_text(encoding="utf-8")
        task_script = Path("frontend/js/task-page.js").read_text(encoding="utf-8")
        viewer_script = Path("frontend/js/viewer-page.js").read_text(encoding="utf-8")

        self.assertIn("createTask", create_script)
        self.assertIn("occasion:", create_script)
        self.assertIn("relationship:", create_script)
        self.assertIn("gift_message:", create_script)
        self.assertIn("favorite_color:", create_script)
        self.assertIn("fetchTask", task_script)
        self.assertIn("createViewerRuntime", viewer_script)
        self.assertIn("taskId", task_script)
        self.assertIn("personUrl", viewer_script)


if __name__ == "__main__":
    unittest.main()
