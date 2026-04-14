import unittest
from pathlib import Path


class NavigationShellSmokeTestCase(unittest.TestCase):
    def test_shared_navigation_shell_exists_across_pages(self) -> None:
        nav_js_path = Path("frontend/js/nav.js")
        index_html_path = Path("frontend/index.html")
        gallery_html_path = Path("frontend/gallery.html")
        profile_html_path = Path("frontend/profile.html")
        work_html_path = Path("frontend/work.html")

        self.assertTrue(nav_js_path.exists())
        self.assertTrue(index_html_path.exists())
        self.assertTrue(gallery_html_path.exists())
        self.assertTrue(profile_html_path.exists())
        self.assertTrue(work_html_path.exists())

        nav_js = nav_js_path.read_text(encoding="utf-8")
        index_html = index_html_path.read_text(encoding="utf-8")
        gallery_html = gallery_html_path.read_text(encoding="utf-8")
        profile_html = profile_html_path.read_text(encoding="utf-8")
        work_html = work_html_path.read_text(encoding="utf-8")

        for html in (index_html, gallery_html, profile_html, work_html):
            self.assertIn('data-nav-root', html)
            self.assertIn('./js/nav.js', html)
            self.assertIn('data-nav-link="home"', html)
            self.assertIn('data-nav-link="gallery"', html)
            self.assertIn('data-nav-link="profile"', html)
            self.assertIn('data-nav-auth', html)

        self.assertIn('window.localStorage.getItem("bazi3d.token")', nav_js)
        self.assertIn('window.localStorage.removeItem("bazi3d.token")', nav_js)
        self.assertIn('window.localStorage.removeItem("bazi3d.user")', nav_js)
        self.assertIn('window.location.href = "./auth.html"', nav_js)
        self.assertIn('button.dataset.mode = "logout"', nav_js)
        self.assertIn('button.dataset.mode = "login"', nav_js)
        self.assertIn("aria-current", nav_js)


if __name__ == "__main__":
    unittest.main()
