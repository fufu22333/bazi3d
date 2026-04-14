import unittest
from pathlib import Path


class AuthPageShellSmokeTestCase(unittest.TestCase):
    def test_auth_page_and_guard_hooks_exist(self) -> None:
        auth_html_path = Path("frontend/auth.html")
        auth_js_path = Path("frontend/js/auth.js")
        api_js_path = Path("frontend/js/api.js")
        guard_js_path = Path("frontend/js/modules/auth-guard.js")

        self.assertTrue(auth_html_path.exists())
        self.assertTrue(auth_js_path.exists())
        self.assertTrue(api_js_path.exists())
        self.assertTrue(guard_js_path.exists())

        auth_html = auth_html_path.read_text(encoding="utf-8")
        auth_js = auth_js_path.read_text(encoding="utf-8")
        api_js = api_js_path.read_text(encoding="utf-8")
        guard_js = guard_js_path.read_text(encoding="utf-8")

        self.assertIn('id="login-form"', auth_html)
        self.assertIn('id="register-form"', auth_html)
        self.assertIn('id="auth-status"', auth_html)
        self.assertIn("账号登录", auth_html)
        self.assertIn("注册账号", auth_html)
        self.assertIn("返回创建页", auth_html)

        self.assertIn("loginUser", api_js)
        self.assertIn("registerUser", api_js)
        self.assertIn("getStoredToken", api_js)
        self.assertIn("clearStoredToken", api_js)

        self.assertIn("login-form", auth_js)
        self.assertIn("register-form", auth_js)
        self.assertIn("window.location.href", auth_js)
        self.assertIn("正在登录", auth_js)
        self.assertIn("注册成功", auth_js)

        self.assertIn("requireAuth", guard_js)
        self.assertIn("/auth.html", guard_js)


if __name__ == "__main__":
    unittest.main()
