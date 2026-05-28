import unittest
from pathlib import Path


class ViewerRuntimeShellTestCase(unittest.TestCase):
    def test_runtime_loads_models_through_stable_loader_path(self) -> None:
        runtime_path = Path("frontend/js/viewer/runtime.js")
        script = runtime_path.read_text(encoding="utf-8")

        self.assertIn("function buildLoaderUrl", script)
        self.assertIn("/api/proxy/glb?url=", script)
        self.assertIn("function fitModelToView", script)
        self.assertIn("Box3", script)
        self.assertIn("getSize", script)
        self.assertIn("currentModel", script)

    def test_viewer_page_can_auto_load_query_model(self) -> None:
        page_script = Path("frontend/js/viewer-page.js").read_text(encoding="utf-8")

        self.assertIn("autoLoadModelFromQuery", page_script)
        self.assertIn('params.get("autoload") === "1"', page_script)
        self.assertIn("loadSelectedModel", page_script)


if __name__ == "__main__":
    unittest.main()
