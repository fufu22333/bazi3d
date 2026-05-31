import unittest
from pathlib import Path


class WorkPageShellSmokeTestCase(unittest.TestCase):
    def test_work_page_hooks_exist(self) -> None:
        html_path = Path("frontend/work.html")
        script_path = Path("frontend/js/work.js")
        api_path = Path("frontend/js/api.js")
        runtime_path = Path("frontend/js/viewer/runtime.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(script_path.exists())
        self.assertTrue(api_path.exists())
        self.assertTrue(runtime_path.exists())

        html = html_path.read_text(encoding="utf-8")
        script = script_path.read_text(encoding="utf-8")
        api_script = api_path.read_text(encoding="utf-8")
        runtime_script = runtime_path.read_text(encoding="utf-8")

        self.assertIn('id="work-title"', html)
        self.assertIn('id="work-description"', html)
        self.assertIn('id="work-author"', html)
        self.assertIn('id="work-visibility"', html)
        self.assertIn('id="work-tags"', html)
        self.assertIn('id="work-viewer-status"', html)
        self.assertIn('id="work-manage-panel"', html)
        self.assertIn('id="work-manage-status"', html)
        self.assertIn('id="edit-work-form"', html)
        self.assertIn('id="edit-title"', html)
        self.assertIn('id="edit-description"', html)
        self.assertIn('id="edit-visibility"', html)
        self.assertIn('id="edit-allow-remix"', html)
        self.assertIn('id="save-work"', html)
        self.assertIn('id="delete-work"', html)
        self.assertIn('id="viewer-canvas"', html)
        self.assertIn("作品详情", html)
        self.assertIn("返回画廊", html)
        self.assertIn("作品信息", html)

        self.assertIn("fetchWorkDetail", api_script)
        self.assertIn("updateWorkDetail", api_script)
        self.assertIn("deleteWorkDetail", api_script)
        self.assertIn("createViewerRuntime", runtime_script)
        self.assertIn("loadWorkDetail", script)
        self.assertIn("syncWorkAssetToViewer", script)
        self.assertIn("resourceTypeSelect.value = resourceType", script)
        self.assertIn("guardian-url", script)
        self.assertIn("createViewerRuntime", script)
        self.assertIn("work-title", script)
        self.assertIn("getStoredUser", script)
        self.assertIn("toggleManagePanel", script)
        self.assertIn("handleSaveSubmit", script)
        self.assertIn("handleDeleteClick", script)
        self.assertIn("保存作品修改", script)
        self.assertIn("未找到作品", script)


if __name__ == "__main__":
    unittest.main()
