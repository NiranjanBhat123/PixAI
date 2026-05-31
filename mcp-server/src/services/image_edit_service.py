import base64
import logging
from io import BytesIO

from PIL import Image, ImageEnhance, ImageFilter
from PIL import ImageColor

from src.core.exceptions import ImageProcessingException

logger = logging.getLogger(__name__)


class ImageEditService:
    """
    Single responsibility: apply deterministic image edits using Pillow.
    No AI involved — brightness/contrast/etc. are mathematical operations.
    """

    def apply_edits(
        self,
        image_base64: str,
        brightness: float = 0.0,
        contrast: float = 0.0,
        saturation: float = 0.0,
        sharpness: float = 0.0,
        warmth: float = 0.0
    ) -> str:
        """
        Apply image adjustments and return result as base64 string.
        All values are in range -1.0 to 1.0 where 0.0 = no change.
        """
        try:
            image = self._decode_image(image_base64)
            logger.info("Applying edits: brightness=%.2f, contrast=%.2f, saturation=%.2f, sharpness=%.2f, warmth=%.2f",
                        brightness, contrast, saturation, sharpness, warmth)

            image = self._apply_brightness(image, brightness)
            image = self._apply_contrast(image, contrast)
            image = self._apply_saturation(image, saturation)
            image = self._apply_sharpness(image, sharpness)
            image = self._apply_warmth(image, warmth)

            result = self._encode_image(image)
            logger.info("Image edits applied successfully")
            return result

        except ImageProcessingException:
            raise
        except Exception as e:
            logger.error("Failed to apply image edits: %s", str(e))
            raise ImageProcessingException("Failed to apply image edits.", cause=e)

    # --- Private helpers ---

    def _decode_image(self, image_base64: str) -> Image.Image:
        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            # Ensure RGB for consistent processing (handles PNG with alpha too)
            return image.convert("RGB")
        except Exception as e:
            raise ImageProcessingException("Could not decode image for editing.", cause=e)

    def _encode_image(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=92)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _apply_brightness(self, image: Image.Image, value: float) -> Image.Image:
        if value == 0.0:
            return image
        # Pillow enhancer: 1.0 = original, <1 = darker, >1 = brighter
        factor = 1.0 + value
        factor = max(0.1, min(3.0, factor))  # clamp to safe range
        return ImageEnhance.Brightness(image).enhance(factor)

    def _apply_contrast(self, image: Image.Image, value: float) -> Image.Image:
        if value == 0.0:
            return image
        factor = 1.0 + value
        factor = max(0.1, min(3.0, factor))
        return ImageEnhance.Contrast(image).enhance(factor)

    def _apply_saturation(self, image: Image.Image, value: float) -> Image.Image:
        if value == 0.0:
            return image
        factor = 1.0 + value
        factor = max(0.0, min(3.0, factor))
        return ImageEnhance.Color(image).enhance(factor)

    def _apply_sharpness(self, image: Image.Image, value: float) -> Image.Image:
        if value == 0.0:
            return image
        factor = 1.0 + value
        factor = max(0.0, min(3.0, factor))
        return ImageEnhance.Sharpness(image).enhance(factor)

    def _apply_warmth(self, image: Image.Image, value: float) -> Image.Image:
        """
        Warmth adjusts color temperature.
        Positive = warmer (more red/yellow), Negative = cooler (more blue).
        """
        if value == 0.0:
            return image

        r, g, b = image.split()

        # Warmth: boost red, reduce blue (and vice versa for cooling)
        intensity = int(abs(value) * 30)  # max 30 pixel value shift

        if value > 0:
            r = r.point(lambda px: min(255, px + intensity))
            b = b.point(lambda px: max(0, px - intensity))
        else:
            r = r.point(lambda px: max(0, px - intensity))
            b = b.point(lambda px: min(255, px + intensity))

        return Image.merge("RGB", (r, g, b))