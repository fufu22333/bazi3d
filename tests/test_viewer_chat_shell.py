import unittest
from pathlib import Path


class ViewerChatShellSmokeTestCase(unittest.TestCase):
    def test_chat_ui_and_hooks_exist(self) -> None:
        html_path = Path("frontend/index.html")
        main_js_path = Path("frontend/js/viewer/main.js")
        api_js_path = Path("frontend/js/api.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(main_js_path.exists())
        self.assertTrue(api_js_path.exists())

        html = html_path.read_text(encoding="utf-8")
        main_js = main_js_path.read_text(encoding="utf-8")
        api_js = api_js_path.read_text(encoding="utf-8")

        self.assertIn('id="chat-log"', html)
        self.assertIn('id="chat-input"', html)
        self.assertIn('id="send-chat"', html)

        self.assertIn("sendCharacterChat", api_js)
        self.assertIn("chat-log", main_js)
        self.assertIn("send-chat", main_js)

    def test_chat_ui_uses_bubble_layout_hooks(self) -> None:
        html = Path("frontend/index.html").read_text(encoding="utf-8")
        main_js = Path("frontend/js/viewer/main.js").read_text(encoding="utf-8")

        self.assertIn(".chat-log", html)
        self.assertIn(".chat-message", html)
        self.assertIn(".chat-message--user", html)
        self.assertIn(".chat-message--character", html)
        self.assertIn("overflow-y: auto", html)
        self.assertIn("scrollTop = chatLogNode.scrollHeight", main_js)
        self.assertIn("document.createElement(\"div\")", main_js)
        self.assertNotIn('chatLogNode.textContent = lines.join(" | ")', main_js)


if __name__ == "__main__":
    unittest.main()
