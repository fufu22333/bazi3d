import unittest


class ImageReferenceSupportTestCase(unittest.TestCase):
    def test_prompt_output_allows_image_reference_passthrough(self) -> None:
        from backend.prompt.builder import generate_prompt_output

        input_profile = {
            "display_name": "Aster",
            "style_profile": {
                "fashion_style": "modern casual",
                "spirit_style": "dreamy water",
            },
            "reference_image_url": "https://example.com/reference.png",
        }

        def fake_llm(_: str) -> str:
            return """
            {
              "version": "v1.5",
              "image_reference": "https://example.com/reference.png",
              "character": {
                "style": "modern casual",
                "material": "matte fabric",
                "pose_keywords": ["standing"],
                "visual_keywords": ["layered"],
                "description": "A calm fashion-forward character."
              },
              "guardian_spirit": {
                "style": "dreamy water",
                "material": "translucent mist",
                "pose_keywords": ["floating"],
                "visual_keywords": ["ripple"],
                "description": "A guardian spirit with flowing water energy."
              }
            }
            """

        result = generate_prompt_output(input_profile, fake_llm)

        self.assertEqual(result.image_reference, "https://example.com/reference.png")

    def test_create_task_persists_reference_image_url(self) -> None:
        from backend.app import create_app
        from backend.models import SessionLocal
        from backend.models.input_profile import InputProfile

        app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "image-ref-secret",
            }
        )
        client = app.test_client()

        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "image-ref@example.com",
                "username": "image-ref",
                "password": "pass1234",
            },
        )
        token = register_response.get_json()["token"]

        create_response = client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "display_name": "Aster",
                "gender": "female",
                "birth_location": "Shanghai",
                "reference_image_url": "https://example.com/reference.png",
                "style_profile": {
                    "fashion_style": "modern casual",
                    "spirit_style": "dreamy water",
                },
            },
        )

        self.assertEqual(create_response.status_code, 201)
        profile = SessionLocal().query(InputProfile).one()
        self.assertEqual(
            profile.reference_image_url,
            "https://example.com/reference.png",
        )


if __name__ == "__main__":
    unittest.main()
