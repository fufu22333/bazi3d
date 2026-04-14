import unittest
from pathlib import Path


class ApiShellSmokeTestCase(unittest.TestCase):
    def test_api_wrapper_uses_relative_paths(self) -> None:
        api_path = Path("frontend/js/api.js")

        self.assertTrue(api_path.exists())

        api_script = api_path.read_text(encoding="utf-8")

        self.assertIn('const API_BASE_URL = "";', api_script)
        self.assertNotIn("http://127.0.0.1:8000", api_script)
        self.assertNotIn("http://localhost:8000", api_script)
        self.assertNotIn("http://127.0.0.1:5001", api_script)
        self.assertNotIn("http://localhost:5001", api_script)
        self.assertIn('requestJson("/api/auth/login"', api_script)
        self.assertIn('fetch(`${API_BASE_URL}/api/works/${workId}`', api_script)


if __name__ == "__main__":
    unittest.main()
