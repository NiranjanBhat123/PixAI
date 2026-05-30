import json
import logging
from mcp.server.fastmcp import FastMCP
from src.services.gemini_service import GeminiService
from src.core.models import StyleResult
from src.core.exceptions import GeminiServiceException, ImageProcessingException

logger = logging.getLogger(__name__)


def register_style_tool(mcp: FastMCP, gemini_service: GeminiService) -> None:

    @mcp.tool(
        name="suggest_styles",
        description="Suggests artistic style versions of an image such as Ghibli, B&W, pencil sketch, or cartoon.",
    )
    def suggest_styles(image_base64: str) -> dict:
        """
        Args:
            image_base64: Base64-encoded image string (JPEG or PNG)
        Returns:
            StyleResult with style suggestions ranked by suitability
        """
        logger.info("suggest_styles tool called")
        try:
            raw_json = gemini_service.get_style_suggestions(image_base64)
            parsed = json.loads(raw_json)
            result = StyleResult(**parsed)
            logger.info("Style suggestions generated: %d styles", len(result.suggestions))
            return result.model_dump()
        except (GeminiServiceException, ImageProcessingException) as e:
            logger.error("Style tool failed: %s", str(e))
            return {"error": str(e), "suggestions": []}
        except json.JSONDecodeError as e:
            logger.error("Gemini returned invalid JSON for styles: %s", str(e))
            return {"error": "AI returned an unexpected response format", "suggestions": []}