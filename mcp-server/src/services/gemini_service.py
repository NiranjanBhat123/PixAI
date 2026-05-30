import logging
import os
import base64
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

from src.core.exceptions import GeminiServiceException, ConfigurationException, ImageProcessingException

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Single responsibility: all communication with the Gemini API.
    Constructed once and injected into tools (Dependency Inversion Principle).
    """

    MODEL_NAME = "gemini-3.5-flash"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConfigurationException(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        self._client = genai.Client(api_key=api_key)
        logger.info("GeminiService initialized with model: %s", self.MODEL_NAME)

    def _decode_image(self, image_base64: str) -> Image.Image:
        """Decode a base64 image string into a PIL Image."""
        try:
            image_bytes = base64.b64decode(image_base64)
            return Image.open(BytesIO(image_bytes))
        except Exception as e:
            logger.error("Failed to decode image: %s", str(e))
            raise ImageProcessingException("Could not decode the provided image.", cause=e)

    def _call_gemini(self, prompt: str, image: Image.Image) -> str:
        """
        Core method: sends prompt + image to Gemini, returns raw text.
        All other methods in this service call this one.
        """
        try:
            logger.debug("Calling Gemini with prompt length: %d", len(prompt))
            response = self._client.models.generate_content(
                model=self.MODEL_NAME,
                contents=[prompt, image],
            )
            result = response.text
            logger.debug("Gemini responded with %d characters", len(result))
            return result
        except Exception as e:
            logger.error("Gemini API call failed: %s", str(e))
            raise GeminiServiceException("Gemini API call failed.", cause=e)

    def get_caption_suggestions(self, image_base64: str) -> str:
        """Ask Gemini to suggest captions. Returns raw JSON string."""
        image = self._decode_image(image_base64)
        prompt = """
        Analyze this image and suggest 4 creative captions for it.
        
        Respond ONLY with valid JSON in this exact format, no extra text, no markdown:
        {
            "image_description": "brief description of what you see",
            "suggestions": [
                {"caption": "...", "tone": "funny"},
                {"caption": "...", "tone": "poetic"},
                {"caption": "...", "tone": "minimal"},
                {"caption": "...", "tone": "inspirational"}
            ]
        }
        """
        logger.info("Requesting caption suggestions from Gemini")
        return self._call_gemini(prompt, image)

    def get_edit_suggestions(self, image_base64: str) -> str:
        """Ask Gemini to analyze and suggest image edits. Returns raw JSON string."""
        image = self._decode_image(image_base64)
        prompt = """
        Analyze this image's technical qualities like brightness, contrast, saturation, sharpness, and warmth.
        Suggest specific adjustments that would improve it.
        
        Respond ONLY with valid JSON in this exact format, no extra text, no markdown:
        {
            "overall_assessment": "brief overall quality assessment",
            "suggestions": [
                {
                    "parameter": "brightness",
                    "current_estimate": "slightly dark",
                    "suggested_value": 0.2,
                    "reason": "The image would benefit from more light"
                }
            ]
        }
        Values must be between -1.0 (decrease a lot) and 1.0 (increase a lot).
        """
        logger.info("Requesting edit suggestions from Gemini")
        return self._call_gemini(prompt, image)

    def get_style_suggestions(self, image_base64: str) -> str:
        """Ask Gemini to suggest artistic style versions. Returns raw JSON string."""
        image = self._decode_image(image_base64)
        prompt = """
        Look at this image and suggest which artistic styles would suit it best.
        Consider: black_and_white, ghibli, pencil_sketch, cartoon.
        
        Respond ONLY with valid JSON in this exact format, no extra text, no markdown:
        {
            "suggestions": [
                {
                    "style": "black_and_white",
                    "description": "how this specific image would look in this style",
                    "appeal": "why this style suits this particular image"
                }
            ]
        }
        Suggest all 4 styles, ranked by how well they suit this image.
        """
        logger.info("Requesting style suggestions from Gemini")
        return self._call_gemini(prompt, image)