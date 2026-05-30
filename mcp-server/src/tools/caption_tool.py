import json
import logging
from mcp.server.fastmcp import FastMCP
from src.services.gemini_service import GeminiService
from src.core.models import CaptionResult
from src.core.exceptions import GeminiServiceException, ImageProcessingException

logger = logging.getLogger(__name__)


def register_caption_tool(mcp: FastMCP, gemini_service: GeminiService) -> None:
    """
    Registers the caption suggestion tool onto the MCP server.
    """

    @mcp.tool(
        name="suggest_captions",
        description="Analyzes an image and suggests creative captions with different tones.",
    )
    def suggest_captions(image_base64: str) -> dict:
        """
        Args:
            image_base64: Base64-encoded image string (JPEG or PNG)
        Returns:
            CaptionResult with suggestions and image description
        """
        logger.info("suggest_captions tool called")
        try:
            raw_json = gemini_service.get_caption_suggestions(image_base64)
            parsed = json.loads(raw_json)
            result = CaptionResult(**parsed)
            logger.info("Caption suggestions generated: %d captions", len(result.suggestions))
            return result.model_dump()
        except (GeminiServiceException, ImageProcessingException) as e:
            logger.error("Caption tool failed: %s", str(e))
            return {"error": str(e), "suggestions": []}
        except json.JSONDecodeError as e:
            logger.error("Gemini returned invalid JSON for captions: %s", str(e))
            return {"error": "AI returned an unexpected response format", "suggestions": []}