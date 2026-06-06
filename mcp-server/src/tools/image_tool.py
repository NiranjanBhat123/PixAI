import logging
from mcp.server.fastmcp import FastMCP
from src.services.gemini_service import GeminiService
from src.services.image_edit_service import ImageEditService
from src.services.style_filter_service import StyleFilterService   # ← new import
from src.core.models import ImageResult
from src.core.exceptions import GeminiServiceException, ImageProcessingException

logger = logging.getLogger(__name__)


def register_image_tool(
    mcp: FastMCP,
    gemini_service: GeminiService,
    edit_service: ImageEditService,
    filter_service: StyleFilterService       
) -> None:

    @mcp.tool(
        name="apply_image_edits",
        description="Apply brightness, contrast, saturation, sharpness and warmth adjustments to an image.",
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
            return ImageResult(
                image_base64=result_base64,
                format="jpeg",
                message=f"Edits applied: brightness={brightness}, contrast={contrast}, saturation={saturation}"
            ).model_dump()
        except ImageProcessingException as e:
            logger.error("Image edit failed: %s", str(e))
            return {"error": str(e), "image_base64": "", "format": "jpeg", "message": str(e)}

    @mcp.tool(
        name="apply_style_filter",
        description="Apply an artistic Pillow filter to an image. Styles: pencil_sketch, vintage, oil_painting, emboss.",
    )
    def apply_style_filter(
        image_base64: str,
        style: str
    ) -> dict:
        logger.info("apply_style_filter tool called: style=%s", style)
        try:
            result_base64 = filter_service.apply_style(image_base64, style)
            return ImageResult(
                image_base64=result_base64,
                format="jpeg",
                message=f"Applied {style} style to your image."
            ).model_dump()
        except ImageProcessingException as e:
            logger.error("Style filter failed: %s", str(e))
            return {"error": str(e), "image_base64": "", "format": "jpeg", "message": str(e)}