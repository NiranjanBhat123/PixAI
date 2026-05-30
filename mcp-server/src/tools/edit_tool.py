import json
import logging
from mcp.server.fastmcp import FastMCP
from src.services.gemini_service import GeminiService
from src.core.models import EditResult
from src.core.exceptions import GeminiServiceException, ImageProcessingException

logger = logging.getLogger(__name__)


def register_edit_tool(mcp: FastMCP, gemini_service: GeminiService) -> None:

    @mcp.tool(
        name="suggest_edits",
        description="Analyzes an image and suggests specific technical edits like brightness, contrast, saturation.",
    )
    def suggest_edits(image_base64: str) -> dict:
        """
        Args:
            image_base64: Base64-encoded image string (JPEG or PNG)
        Returns:
            EditResult with parameter suggestions and overall assessment
        """
        logger.info("suggest_edits tool called")
        try:
            raw_json = gemini_service.get_edit_suggestions(image_base64)
            parsed = json.loads(raw_json)
            result = EditResult(**parsed)
            logger.info("Edit suggestions generated: %d suggestions", len(result.suggestions))
            return result.model_dump()
        except (GeminiServiceException, ImageProcessingException) as e:
            logger.error("Edit tool failed: %s", str(e))
            return {"error": str(e), "suggestions": []}
        except json.JSONDecodeError as e:
            logger.error("Gemini returned invalid JSON for edits: %s", str(e))
            return {"error": "AI returned an unexpected response format", "suggestions": []}