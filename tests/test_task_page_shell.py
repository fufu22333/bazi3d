import unittest
from pathlib import Path


class TaskPageShellSmokeTestCase(unittest.TestCase):
    def test_task_page_hooks_and_api_wrapper_exist(self) -> None:
        html_path = Path("frontend/index.html")
        viewer_path = Path("frontend/js/viewer/main.js")
        api_path = Path("frontend/js/api.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(viewer_path.exists())
        self.assertTrue(api_path.exists())

        html = html_path.read_text(encoding="utf-8")
        viewer_script = viewer_path.read_text(encoding="utf-8")
        api_script = api_path.read_text(encoding="utf-8")

        self.assertIn('id="task-form"', html)
        self.assertIn('id="create-layout"', html)
        self.assertIn('id="create-input-panel"', html)
        self.assertIn('id="create-status-panel"', html)
        self.assertIn('id="create-viewer-panel"', html)
        self.assertIn('id="basic-profile-section"', html)
        self.assertIn('id="style-profile-section"', html)
        self.assertIn('id="result-placeholder"', html)
        self.assertIn('id="viewer-display-shell"', html)
        self.assertIn('id="display-name"', html)
        self.assertIn('id="gender"', html)
        self.assertIn('id="birth-location"', html)
        self.assertIn('id="birth-datetime"', html)
        self.assertIn('id="reference-image-url"', html)
        self.assertIn('id="fashion-style"', html)
        self.assertIn('id="spirit-style"', html)
        self.assertIn('id="extra-note"', html)
        self.assertIn('id="task-status"', html)
        self.assertIn('id="task-meta"', html)
        self.assertIn('id="task-hint"', html)
        self.assertIn('id="task-detail-link"', html)
        self.assertNotIn('id="auth-token"', html)
        self.assertIn('data-nav-root', html)
        self.assertNotIn('id="auth-link"', html)
        self.assertNotIn('id="logout-button"', html)

        self.assertIn("createTask", api_script)
        self.assertIn("fetchTask", api_script)
        self.assertIn("getStoredToken", api_script)

        self.assertIn("startTaskPolling", viewer_script)
        self.assertIn("syncAssetsToViewer", viewer_script)
        self.assertIn("autoLoadCompletedCharacter", viewer_script)
        self.assertIn('resourceTypeSelect.value = "person"', viewer_script)
        self.assertIn("reference_image_url", viewer_script)
        self.assertIn("free_text", viewer_script)
        self.assertIn("extraNoteInput", viewer_script)
        self.assertIn("taskDetailLink", viewer_script)
        self.assertIn("task.html?taskId=", viewer_script)
        self.assertIn("restoreTaskFromNavigation", viewer_script)
        self.assertIn('initialParams.get("taskId")', viewer_script)
        self.assertIn("hydrateFormFromTask", viewer_script)
        self.assertIn("requireAuth", viewer_script)
        self.assertIn("renderTaskState", viewer_script)
        self.assertIn("setResultPlaceholder", viewer_script)
        self.assertNotIn("authLink", viewer_script)
        self.assertNotIn("logoutButton", viewer_script)
        self.assertIn("提交任务", html)
        self.assertIn("尚未生成资源", html)

    def test_task_page_preserves_task_context_when_returning_home(self) -> None:
        nav_script = Path("frontend/js/nav.js").read_text(encoding="utf-8")
        task_script = Path("frontend/js/task-page.js").read_text(encoding="utf-8")

        self.assertIn("resolveLastTaskId", nav_script)
        self.assertIn("withTaskContext", nav_script)
        self.assertIn("bazi3d.lastTaskId", nav_script)
        self.assertIn("updateReturnToCreateLink", task_script)
        self.assertIn('data-nav-link="home"', task_script)


if __name__ == "__main__":
    unittest.main()
