import unittest
from pathlib import Path


class ViewerInteractionShellSmokeTestCase(unittest.TestCase):
    def test_skybox_and_interaction_hooks_exist(self) -> None:
        html_path = Path("frontend/index.html")
        main_js_path = Path("frontend/js/viewer/main.js")
        skybox_js_path = Path("frontend/js/viewer/skybox.js")
        interaction_js_path = Path("frontend/js/viewer/interaction.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(main_js_path.exists())
        self.assertTrue(skybox_js_path.exists())
        self.assertTrue(interaction_js_path.exists())

        html = html_path.read_text(encoding="utf-8")
        main_js = main_js_path.read_text(encoding="utf-8")
        skybox_js = skybox_js_path.read_text(encoding="utf-8")
        interaction_js = interaction_js_path.read_text(encoding="utf-8")

        self.assertIn('id="skybox-url"', html)
        self.assertIn('id="interaction-status"', html)
        self.assertIn('id="motion-status"', html)
        self.assertIn('id="trigger-greet"', html)

        self.assertIn("applySkyboxBackground", main_js)
        self.assertIn("attachModelInteraction", main_js)
        self.assertIn("motion-status", main_js)
        self.assertIn("trigger-greet", main_js)
        self.assertIn("playClip(\"wave\")", main_js)

        self.assertIn("applySkyboxBackground", skybox_js)
        self.assertIn("EquirectangularReflectionMapping", skybox_js)

        self.assertIn("attachModelInteraction", interaction_js)
        self.assertIn("Raycaster", interaction_js)
        self.assertIn("pointerdown", interaction_js)
        self.assertIn("model selected", interaction_js)


if __name__ == "__main__":
    unittest.main()
