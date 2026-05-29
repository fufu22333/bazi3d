import re
import unittest
from pathlib import Path


class FrontendBrandingTestCase(unittest.TestCase):
    def test_html_pages_do_not_expose_project_codename(self) -> None:
        pattern = re.compile(r"bazi\s*3d|bazi3d", re.IGNORECASE)

        for html_path in Path("frontend").glob("*.html"):
            with self.subTest(page=str(html_path)):
                html = html_path.read_text(encoding="utf-8")
                self.assertIsNone(pattern.search(html))


if __name__ == "__main__":
    unittest.main()
