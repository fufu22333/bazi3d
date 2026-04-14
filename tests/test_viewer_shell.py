import unittest
from pathlib import Path


class ViewerShellSmokeTestCase(unittest.TestCase):
    def test_viewer_shell_files_and_hooks_exist(self) -> None:
        html_path = Path("frontend/index.html")
        js_path = Path("frontend/js/viewer/main.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(js_path.exists())

        html = html_path.read_text(encoding="utf-8")
        script = js_path.read_text(encoding="utf-8")

        self.assertIn('id="person-url"', html)
        self.assertIn('id="guardian-url"', html)
        self.assertIn('id="person-file"', html)
        self.assertIn('id="guardian-file"', html)
        self.assertIn('accept=".glb,.fbx,.obj,model/gltf-binary"', html)
        self.assertIn("或填写链接", html)
        self.assertIn('id="resource-type"', html)
        self.assertIn('id="load-model"', html)
        self.assertIn('id="viewer-canvas"', html)
        self.assertIn('js/viewer/main.js', html)

        self.assertIn("GLTFLoader", script)
        self.assertIn("OrbitControls", script)
        self.assertIn("loadSelectedModel", script)
        self.assertIn("URL.createObjectURL", script)
        self.assertIn("当前仅支持 GLB 格式", script)
        self.assertIn("/api/proxy/glb?url=", script)


if __name__ == "__main__":
    unittest.main()
