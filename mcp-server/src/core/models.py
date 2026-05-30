from pydantic import BaseModel, Field
from enum import Enum


class StyleType(str, Enum):
    BLACK_AND_WHITE = "black_and_white"
    GHIBLI = "ghibli"
    PENCIL_SKETCH = "pencil_sketch"
    CARTOON = "cartoon"


class CaptionSuggestion(BaseModel):
    caption: str = Field(description="A suggested caption for the image")
    tone: str = Field(description="The tone of this caption e.g. funny, poetic, minimal")


class CaptionResult(BaseModel):
    suggestions: list[CaptionSuggestion] = Field(description="List of caption suggestions")
    image_description: str = Field(description="Brief description of what Gemini saw in the image")


class EditSuggestion(BaseModel):
    parameter: str = Field(description="Edit parameter e.g. brightness, contrast, saturation")
    current_estimate: str = Field(description="Estimated current state e.g. slightly dark")
    suggested_value: float = Field(description="Suggested adjustment value between -1.0 and 1.0")
    reason: str = Field(description="Why this edit would improve the image")


class EditResult(BaseModel):
    suggestions: list[EditSuggestion] = Field(description="List of edit suggestions")
    overall_assessment: str = Field(description="Overall assessment of the image quality")


class StyleSuggestion(BaseModel):
    style: StyleType
    description: str = Field(description="How this style would look for this specific image")
    appeal: str = Field(description="Why this style would suit this image")


class StyleResult(BaseModel):
    suggestions: list[StyleSuggestion] = Field(description="List of style version suggestions")