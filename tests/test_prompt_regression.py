import json
import unittest
from pathlib import Path


FIXTURE_PATH = Path("tests/fixtures/golden_inputs.json")


class PromptRegressionTestCase(unittest.TestCase):
    def test_golden_inputs_keep_prompt_and_json_contract_stable(self) -> None:
        from backend.prompt.builder import build_prompt, generate_prompt_output

        fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(fixtures), 3)
        self.assertLessEqual(len(fixtures), 5)

        for fixture in fixtures:
            with self.subTest(case=fixture["name"]):
                prompt = build_prompt(fixture["input_profile"])
                for fragment in fixture["expected_prompt_fragments"]:
                    self.assertIn(fragment, prompt)

                def fake_llm(_: str) -> str:
                    return json.dumps(fixture["mock_llm_response"])

                result = generate_prompt_output(fixture["input_profile"], fake_llm)

                self.assertEqual(result.version, "v1")
                self.assertTrue(result.character.pose_keywords)
                self.assertTrue(result.character.visual_keywords)
                self.assertTrue(result.guardian_spirit.pose_keywords)
                self.assertTrue(result.guardian_spirit.visual_keywords)


if __name__ == "__main__":
    unittest.main()
