class PixAIBaseException(Exception):
    """Base exception for all PixAI MCP server errors."""
    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


class GeminiServiceException(PixAIBaseException):
    """Raised when Gemini API calls fail."""
    pass


class ImageProcessingException(PixAIBaseException):
    """Raised when image decoding or validation fails."""
    pass


class ConfigurationException(PixAIBaseException):
    """Raised when required config (e.g. API key) is missing."""
    pass