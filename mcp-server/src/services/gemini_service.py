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
        image = self._decode_image(image_base64)
        prompt = """
        Look at this image and suggest which of these 4 artistic styles would suit it best:
        pencil_sketch, vintage, oil_painting, emboss

        Respond ONLY with valid JSON in this exact format, no extra text, no markdown:
        {
            "suggestions": [
                {
                    "style": "pencil_sketch",
                    "description": "how this specific image would look in this style",
                    "appeal": "why this style suits this particular image"
                }
            ]
        }
        Suggest all 4 styles, ranked by how well they suit this image.
        Use ONLY these exact style names: pencil_sketch, vintage, oil_painting, emboss
        """
        logger.info("Requesting style suggestions from Gemini")
        return self._call_gemini(prompt, image)
    
    def generate_styled_image(self, image_base64: str, style: str, style_description: str) -> str:
        import time
        start_time = time.time()

        # Decode to bytes — NOT PIL Image
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise ImageProcessingException("Could not decode image.", cause=e)

        style_prompts = {
            "ghibli": "Transform this image into Studio Ghibli anime style. Use soft watercolor-like textures, warm lighting, gentle expressive features. Preserve the people, composition and setting.",
            "black_and_white": "Convert this image to a beautiful high-contrast black and white photograph. Emphasize textures, shadows and light. Keep all subjects and composition.",
            "pencil_sketch": "Transform this image into a detailed pencil sketch drawing. Use fine graphite lines, cross-hatching for shadows, clean linework for faces and details.",
            "cartoon": "Transform this into a vibrant cartoon illustration with bold clean outlines, flat bright colors, and friendly expressive faces. Keep the original composition.",
        }

        prompt = style_prompts.get(
            style.lower(),
            f"Transform this image in the style of: {style_description}. Preserve the people and composition."
        )

        logger.info("Generating styled image: style=%s, image_size=%d bytes", style, len(image_base64))

        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

            logger.info("Calling Gemini image generation API...")
            response = self._client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt, image_part],                       # ← fixed image format
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                )
            )

            elapsed = time.time() - start_time
            logger.info("Gemini responded after %.2f seconds", elapsed)

            if not response.candidates:
                raise GeminiServiceException(f"No candidates returned by Gemini for style: {style}")

            for i, part in enumerate(response.candidates[0].content.parts):
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    result_bytes = part.inline_data.data
                    logger.info("Styled image generated: style=%s, time=%.2fs, size=%d bytes",
                                style, elapsed, len(result_bytes))
                    return base64.b64encode(result_bytes).decode("utf-8")

            raise GeminiServiceException(f"No image data in Gemini response for style: {style}")

        except GeminiServiceException:
            raise
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("Style generation failed for %s after %.2fs: %s", style, elapsed, str(e))
            raise GeminiServiceException(f"Style generation failed for {style}.", cause=e)