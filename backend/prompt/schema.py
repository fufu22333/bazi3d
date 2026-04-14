from pydantic import BaseModel, Field


class PromptSection(BaseModel):
    style: str
    material: str
    pose_keywords: list[str] = Field(min_length=1)
    visual_keywords: list[str] = Field(min_length=1)
    description: str


class PromptOutput(BaseModel):
    version: str
    image_reference: str | None = None
    character: PromptSection
    guardian_spirit: PromptSection
