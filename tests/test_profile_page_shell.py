import unittest
from pathlib import Path


class ProfilePageShellSmokeTestCase(unittest.TestCase):
    def test_profile_page_and_management_hooks_exist(self) -> None:
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
        self.assertIn('id="profile-work-count"', html)
        self.assertIn('id="profile-public-count"', html)
        self.assertIn('id="profile-asset-count"', html)
        self.assertIn("我的作品管理", html)
        self.assertIn("作品管理台", html)
        self.assertIn("已发布作品", html)
        self.assertIn("管理说明", html)

        self.assertIn("fetchMyWorks", api_script)
        self.assertIn("getStoredUser", api_script)
        self.assertIn("requireAuth", guard_script)

        self.assertIn("loadProfilePage", script)
        self.assertIn("fetchMyWorks", script)
        self.assertIn("profile-works-list", script)
        self.assertIn("profile-work-count", script)
        self.assertIn("profile-public-count", script)
        self.assertIn("profile-asset-count", script)
        self.assertIn("work-row", script)
        self.assertIn('autoload: "1"', script)
        self.assertIn("work.html?id=", script)
        self.assertNotIn("毕业论文", script)


if __name__ == "__main__":
    unittest.main()
