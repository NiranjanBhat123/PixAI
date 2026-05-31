import logging
from mcp.server.fastmcp import FastMCP
from src.services.gemini_service import GeminiService
from src.services.image_edit_service import ImageEditService
from src.core.models import ImageResult
from src.core.exceptions import GeminiServiceException, ImageProcessingException

logger = logging.getLogger(__name__)


def register_image_tool(mcp: FastMCP, gemini_service: GeminiService, edit_service: ImageEditService) -> None:

    @mcp.tool(
        name="apply_image_edits",
        description="Apply brightness, contrast, saturation, sharpness and warmth adjustments to an image. Returns the edited image as base64.",
    )
    def apply_image_edits(
        image_base64: str,
        brightness: float = 0.0,
        contrast: float = 0.0,
        saturation: float = 0.0,
        sharpness: float = 0.0,
        warmth: float = 0.0
    ) -> dict:
        logger.info("apply_image_edits tool called")
        try:
            result_base64 = edit_service.apply_edits(
                image_base64=image_base64,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                sharpness=sharpness,
                warmth=warmth
            )
            result = ImageResult(
                image_base64=result_base64,
                format="jpeg",
                message=f"Edits applied: brightness={brightness}, contrast={contrast}, saturation={saturation}"
            )
            logger.info("Image edits applied successfully")
            return result.model_dump()
        except ImageProcessingException as e:
            logger.error("Image edit failed: %s", str(e))
            return {"error": str(e), "image_base64": ""}

    @mcp.tool(
        name="generate_styled_image",
        description="Generate an artistic styled version of an image. Styles: ghibli, black_and_white, pencil_sketch, cartoon.",
    )
    def generate_styled_image(
        image_base64: str,
        style: str,
        style_description: str = ""
    ) -> dict:
        logger.info("generate_styled_image tool called for style: %s", style)
        try:
            result_base64 = gemini_service.generate_styled_image(
                image_base64=image_base64,
                style=style,
                style_description=style_description
            )
            result = ImageResult(
                image_base64=result_base64,
                format="jpeg",
                message=f"Generated {style} version of your image."
            )
            logger.info("Styled image generated successfully: %s", style)
            return result.model_dump()
        except (GeminiServiceException, ImageProcessingException) as e:
            logger.error("Style generation failed: %s", str(e))
            return {"error": str(e), "image_base64": ""}