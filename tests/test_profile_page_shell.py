import unittest
from pathlib import Path


class ProfilePageShellSmokeTestCase(unittest.TestCase):
    def test_profile_page_and_data_hooks_exist(self) -> None:
        html_path = Path("frontend/profile.html")
        script_path = Path("frontend/js/profile.js")
        api_path = Path("frontend/js/api.js")
        guard_path = Path("frontend/js/modules/auth-guard.js")

        self.assertTrue(html_path.exists())
        self.assertTrue(script_path.exists())
        self.assertTrue(api_path.exists())
        self.assertTrue(guard_path.exists())

        html = html_path.read_text(encoding="utf-8")
        script = script_path.read_text(encoding="utf-8")
        api_script = api_path.read_text(encoding="utf-8")
        guard_script = guard_path.read_text(encoding="utf-8")

        self.assertIn('id="profile-status"', html)
        self.assertIn('id="profile-username"', html)
        self.assertIn('id="profile-email"', html)
        self.assertIn('id="profile-works-list"', html)
        self.assertIn("我的作品", html)
        self.assertIn("作品集合", html)

        self.assertIn("fetchMyWorks", api_script)
        self.assertIn("getStoredUser", api_script)
        self.assertIn("requireAuth", guard_script)

        self.assertIn("loadProfilePage", script)
        self.assertIn("fetchMyWorks", script)
        self.assertIn("profile-works-list", script)
        self.assertIn("work.html?id=", script)
        self.assertIn("已登录用户", script)
        self.assertIn("加载你的作品", script)


if __name__ == "__main__":
    unittest.main()
