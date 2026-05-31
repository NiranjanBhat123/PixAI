import logging
import sys
import os

# Ensure the mcp-server root is on the path regardless of how this file is invoked
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from src.services.gemini_service import GeminiService
from src.services.image_edit_service import ImageEditService
from src.tools.caption_tool import register_caption_tool
from src.tools.edit_tool import register_edit_tool
from src.tools.style_tool import register_style_tool
from src.tools.image_tool import register_image_tool
import uvicorn


load_dotenv()

# --- Logging setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    logger.info("Initializing PixAI MCP Server...")

    mcp = FastMCP(
        name="pixai-mcp-server",
        instructions="You are PixAI, a creative assistant that helps users with image captions, edits, and artistic styles.",
    )

    gemini_service = GeminiService()
    edit_service = ImageEditService()
    register_caption_tool(mcp, gemini_service)
    register_edit_tool(mcp, gemini_service)
    register_style_tool(mcp, gemini_service)
    register_image_tool(mcp, gemini_service, edit_service)

    logger.info("PixAI MCP Server ready with tools: captions, edits, styles, image_generation")
    return mcp

mcp = create_server()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["sse", "stdio"], default="sse")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "stdio":
        logger.info("Starting PixAI MCP Server with STDIO transport...")
        mcp.run(transport="stdio")
    else:
        logger.info(f"Starting PixAI MCP Server with SSE transport on {args.host}:{args.port}...")
        uvicorn.run(mcp.sse_app(), host=args.host, port=args.port)

