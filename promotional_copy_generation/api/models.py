"""API request/response models."""

from typing import Any

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Generate request."""

    requirements: str = Field(..., description="Promotional requirements")
    description: str | None = Field(None, description="Detailed description")
    platform: str | None = Field(None, description="Target platform")
    style: str | None = Field(None, description="Style preference")
    need_reference: bool = Field(True, description="Whether to retrieve references")
    need_images: bool = Field(False, description="Whether to generate images")


class GenerateResponse(BaseModel):
    """Generate response."""

    copy_text: str = Field(..., description="Promotional copy", serialization_alias="copy")
    image_prompts: list[str] | None = Field(None, description="Image prompts")
    generated_images: list[str] | None = Field(None, description="Generated images as Base64")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")
    error: str | None = Field(None, description="Error message (if any)")
