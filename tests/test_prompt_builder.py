import unittest

from pydantic import ValidationError


class PromptBuilderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.input_profile = {
            "display_name": "Aster",
            "gender": "female",
            "birth_location": "Shanghai",
            "reference_image_url": "https://example.com/reference.png",
            "style_profile": {
                "fashion_style": "modern casual",
                "spirit_style": "dreamy water",
            },
            "extra_payload": {
                "personality_tags": ["calm", "observant"],
                "scene_preference": "misty lakeside",
                "free_text": "soft silhouette with layered accessories",
            },
        }

    def test_build_prompt_uses_template_and_profile_content(self) -> None:
        from backend.prompt.builder import build_prompt

        prompt = build_prompt(self.input_profile)

        self.assertIn("Aster", prompt)
        self.assertIn("modern casual", prompt)
        self.assertIn("dreamy water", prompt)
        self.assertIn("https://example.com/reference.png", prompt)
        self.assertIn('"version"', prompt)

    def test_build_prompt_contains_character_design_constraints(self) -> None:
        from backend.prompt.builder import build_prompt

        prompt = build_prompt(self.input_profile)

        self.assertIn(
            "You are an AI costume designer combining Chinese Bazi astrology with modern 3D character design.",
            prompt,
        )
        self.assertIn(
            'Append at the end exactly: "High detail render, realistic fabric texture, full-body 3D model, cinematic lighting, soft volumetric light."',
            prompt,
        )
        self.assertIn('"character": {', prompt)
        self.assertIn('"style": "string"', prompt)
        self.assertIn('"material": "string"', prompt)
        self.assertIn('"pose_keywords": ["string"]', prompt)
        self.assertIn('"visual_keywords": ["string"]', prompt)
        self.assertIn('"description": "string"', prompt)

    def test_build_prompt_contains_guardian_spirit_constraints(self) -> None:
        from backend.prompt.builder import build_prompt

        prompt = build_prompt(self.input_profile)

        self.assertIn(
            "You are an AI guardian spirit designer combining personality analysis with 3D character design.",
            prompt,
        )
        self.assertIn(
            "Design a guardian spirit companion that visually complements the character's outfit in color palette and material tone.",
            prompt,
        )
        self.assertIn(
            'Append at the end exactly: "High detail render, realistic texture, full-body 3D model, cinematic lighting, soft volumetric light."',
            prompt,
        )
        self.assertIn(
            "Spirit visual style must complement the character's color palette and material tone",
            prompt,
        )
        self.assertIn(
            "The guardian spirit MUST NOT be humanoid or human-shaped",
            prompt,
        )
        self.assertIn(
            "The guardian spirit MUST be a non-human creature: animal, beast, elemental, or fantastical being",
            prompt,
        )
        self.assertIn(
            "The guardian spirit MUST be depicted as a complete full-body creature, not a bust or half-body",
            prompt,
        )
        self.assertIn(
            "Explicitly state the creature is small to medium sized, suitable for a companion role",
            prompt,
        )

    def test_build_prompt_uses_non_empty_style_defaults(self) -> None:
        from backend.prompt.builder import build_prompt

        prompt = build_prompt(
            {
                "display_name": "Aster",
                "style_profile": {},
                "extra_payload": {},
            }
        )

        self.assertIn("- fashion_style: unspecified outfit style", prompt)
        self.assertIn("- spirit_style: unspecified spirit style", prompt)

    def test_generate_prompt_output_validates_legal_llm_json(self) -> None:
        from backend.prompt.builder import generate_prompt_output

        def fake_llm(_: str) -> str:
            return """
            {
              "version": "v1",
              "image_reference": "https://example.com/reference.png",
              "character": {
                "style": "modern casual",
                "material": "matte fabric",
                "pose_keywords": ["standing", "relaxed"],
                "visual_keywords": ["layered", "soft light"],
                "description": "A calm fashion-forward character."
              },
              "guardian_spirit": {
                "style": "dreamy water",
                "material": "translucent mist",
                "pose_keywords": ["floating", "spiraling"],
                "visual_keywords": ["ripple", "glow"],
                "description": "A guardian spirit with flowing water energy."
              }
            }
            """

        result = generate_prompt_output(self.input_profile, fake_llm)

        self.assertEqual(result.version, "v1")
        self.assertEqual(result.image_reference, "https://example.com/reference.png")
        self.assertEqual(result.character.style, "modern casual")
        self.assertEqual(result.guardian_spirit.style, "dreamy water")

    def test_generate_prompt_output_rejects_invalid_json_payload(self) -> None:
        from backend.prompt.builder import generate_prompt_output

        def fake_llm(_: str) -> str:
            return '{"version":"v1","character":{"style":"x"}}'

        with self.assertRaises(ValidationError):
            generate_prompt_output(self.input_profile, fake_llm)


if __name__ == "__main__":
    unittest.main()
