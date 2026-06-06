import base64
import logging
from io import BytesIO

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops

from src.core.exceptions import ImageProcessingException

logger = logging.getLogger(__name__)


class StyleFilterService:
    """
    Single responsibility: apply artistic Pillow-based style filters.
    No AI — all deterministic image processing.
    """

    SUPPORTED_STYLES = ["pencil_sketch", "vintage", "oil_painting", "emboss"]

    def apply_style(self, image_base64: str, style: str) -> str:
        """Apply a named style filter and return base64 result."""
        try:
            image = self._decode_image(image_base64)
            logger.info("Applying style filter: %s", style)

            style_map = {
                "pencil_sketch": self._pencil_sketch,
                "vintage":       self._vintage,
                "oil_painting":  self._oil_painting,
                "emboss":        self._emboss,
            }

            filter_fn = style_map.get(style.lower())
            if not filter_fn:
                raise ImageProcessingException(
                    f"Unknown style: '{style}'. Supported: {self.SUPPORTED_STYLES}"
                )

            result = filter_fn(image)
            encoded = self._encode_image(result)
            logger.info("Style filter '%s' applied successfully", style)
            return encoded

        except ImageProcessingException:
            raise
        except Exception as e:
            logger.error("Style filter failed for '%s': %s", style, str(e))
            raise ImageProcessingException(f"Failed to apply {style} filter.", cause=e)

    # ── Private helpers ──────────────────────────────────────────────

    def _decode_image(self, image_base64: str) -> Image.Image:
        try:
            return Image.open(BytesIO(base64.b64decode(image_base64))).convert("RGB")
        except Exception as e:
            raise ImageProcessingException("Could not decode image.", cause=e)

    def _encode_image(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=92)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _pencil_sketch(self, image: Image.Image) -> Image.Image:
        """Grayscale + color dodge blend — convincing hand-drawn look."""
        gray = image.convert("L")
        inverted = ImageOps.invert(gray)
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=21))

        gray_arr = np.array(gray, dtype=np.float32)
        blur_arr = np.array(blurred, dtype=np.float32)
        denominator = 255.0 - blur_arr
        denominator[denominator == 0] = 1.0  # avoid divide-by-zero

        sketch = np.clip((gray_arr * 255.0) / denominator, 0, 255).astype(np.uint8)
        return Image.fromarray(sketch)

    def _vintage(self, image: Image.Image) -> Image.Image:
        """Faded film look: desaturated, warm, vignetted."""
        # Reduce saturation
        img = ImageEnhance.Color(image).enhance(0.75)
        # Lift shadows (fade blacks — classic film look)
        img = img.point(lambda px: int(px * 0.87 + 22))
        # Warm tint
        r, g, b = img.split()
        r = r.point(lambda px: min(255, px + 18))
        g = g.point(lambda px: min(255, px + 6))
        b = b.point(lambda px: max(0, px - 18))
        img = Image.merge("RGB", (r, g, b))
        # Slight contrast boost
        img = ImageEnhance.Contrast(img).enhance(1.15)
        # Vignette
        return self._add_vignette(img, strength=0.55)

    def _oil_painting(self, image: Image.Image) -> Image.Image:
        """Posterize + smooth + edge enhance — painterly texture."""
        # Boost saturation for vivid paint colours
        img = ImageEnhance.Color(image).enhance(1.7)
        # Smooth out details
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        # Reduce colour palette — key to the painted look
        img = ImageOps.posterize(img, 4)
        # Paint-style edge lines
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        # Final colour pop
        img = ImageEnhance.Color(img).enhance(1.2)
        return img

    def _emboss(self, image: Image.Image) -> Image.Image:
        """3D relief with colour preservation."""
        gray = image.convert("L")
        embossed_gray = gray.filter(ImageFilter.EMBOSS)
        # Convert to RGB and blend with original for colour tinting
        embossed_rgb = embossed_gray.convert("RGB")
        result = Image.blend(image, embossed_rgb, alpha=0.65)
        return ImageEnhance.Contrast(result).enhance(1.3)

    def _add_vignette(self, image: Image.Image, strength: float = 0.5) -> Image.Image:
        """Darken edges with a radial gradient."""
        w, h = image.size
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        xx, yy = np.meshgrid(x, y)
        radius = np.sqrt(xx ** 2 + yy ** 2)
        mask_arr = np.clip(1.0 - radius * strength, 0, 1)
        mask = Image.fromarray((mask_arr * 255).astype(np.uint8))

        r, g, b = image.split()
        return Image.merge("RGB", (
            ImageChops.multiply(r, mask),
            ImageChops.multiply(g, mask),
            ImageChops.multiply(b, mask),
        ))