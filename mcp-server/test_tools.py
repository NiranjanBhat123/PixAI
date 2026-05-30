"""
Quick smoke test — calls GeminiService directly to verify
the API key works and all 3 tools respond correctly.
Run with: python3 test_tools.py path/to/any/image.jpg
"""
import sys
import json
import base64
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

def load_image_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_tools.py path/to/image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    print(f"\n📸 Loading image: {image_path}")
    image_base64 = load_image_as_base64(image_path)
    print(f"✅ Image loaded ({len(image_base64)} base64 chars)\n")

    from src.services.gemini_service import GeminiService
    service = GeminiService()

    # --- Test 1: Captions ---
    print("=" * 50)
    print("🧪 TEST 1: suggest_captions")
    print("=" * 50)
    raw = service.get_caption_suggestions(image_base64)
    result = json.loads(raw)
    print(f"Image description: {result['image_description']}")
    for i, s in enumerate(result['suggestions'], 1):
        print(f"  {i}. [{s['tone']}] {s['caption']}")

    # --- Test 2: Edits ---
    print("\n" + "=" * 50)
    print("🧪 TEST 2: suggest_edits")
    print("=" * 50)
    raw = service.get_edit_suggestions(image_base64)
    result = json.loads(raw)
    print(f"Assessment: {result['overall_assessment']}")
    for s in result['suggestions']:
        print(f"  • {s['parameter']}: {s['current_estimate']} → {s['suggested_value']:+.1f} ({s['reason']})")

    # --- Test 3: Styles ---
    print("\n" + "=" * 50)
    print("🧪 TEST 3: suggest_styles")
    print("=" * 50)
    raw = service.get_style_suggestions(image_base64)
    result = json.loads(raw)
    for s in result['suggestions']:
        print(f"  • [{s['style']}] {s['description']}")
        print(f"    Why: {s['appeal']}")

    print("\n✅ All 3 tools working correctly!")

if __name__ == "__main__":
    main()