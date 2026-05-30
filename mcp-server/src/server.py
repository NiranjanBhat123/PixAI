import logging
import sys
import os

# Ensure the mcp-server root is on the path regardless of how this file is invoked
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from src.services.gemini_service import GeminiService
from src.tools.caption_tool import register_caption_tool
from src.tools.edit_tool import register_edit_tool
from src.tools.style_tool import register_style_tool

load_dotenv()

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Factory function: builds the MCP server, wires dependencies.
    This is our composition root.
    """
    logger.info("Initializing PixAI MCP Server...")

    mcp = FastMCP(
        name="pixai-mcp-server",
        instructions="You are PixAI, a creative assistant that helps users with image captions, edits, and artistic styles.",
    )

    # Build shared service once — injected into all tools (DIP)
    gemini_service = GeminiService()

    # Register each tool group
    register_caption_tool(mcp, gemini_service)
    register_edit_tool(mcp, gemini_service)
    register_style_tool(mcp, gemini_service)

    logger.info("PixAI MCP Server ready with tools: captions, edits, styles")
    return mcp


# Module-level variable — required for `mcp dev` to discover the server
mcp = create_server()

if __name__ == "__main__":
    mcp.run(transport="stdio")