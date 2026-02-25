# pdf_to_markdown_paddle_jp.py
"""
PDF → Markdown using PaddleOCR PP-StructureV3 (Japanese optimized)

- Works with scanned PDFs
- Detects layout blocks (text, title, table, figure, etc.)
- Extracts tables as embedded HTML (Markdown-compatible)
- Outputs structured Markdown with page separation
- Saves to /Users/admin/LG/Markdown/data/dump

Requires: paddlepaddle (CPU version), paddleocr >=3.0, pdf2image, opencv-python
"""

import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from pathlib import Path
import cv2
import numpy as np
from pdf2image import convert_from_bytes

from paddleocr import PPStructureV3

class TextExtractionError(Exception):
    pass

DUMP_DIR = Path("/Users/admin/LG/Markdown/data/dump")

# Initialize structure/layout + table engine (modern V3 pipeline)
structure_engine = PPStructureV3(
    lang="japan",
    use_doc_orientation_classify=True,   # Helps with rotated/scanned pages
    use_doc_unwarping=True,              # Corrects perspective distortion
    # Optional: use_table_recognition=True (default), etc.
)


def convert_pdf_to_images(pdf_bytes: bytes):
    """Convert PDF bytes to list of PIL images (RGB)"""
    return convert_from_bytes(pdf_bytes, dpi=300)


def process_page(image):
    """
    Run PP-StructureV3 pipeline on a single page image
    Returns Markdown-formatted string for that page
    """
    # Convert PIL (RGB) → OpenCV BGR numpy array
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    try:
        # Call the pipeline correctly: .predict(input=...)
        # For single image (numpy array), it returns list of dicts
        result = structure_engine.predict(input=img)
    except Exception as e:
        return f"(Error processing page: {str(e)})"

    markdown_blocks = []

    for block in result:
        block_type = block.get("type", "").strip()

        # Optional debug: uncomment to inspect
        # print(f"Debug: Block type = {block_type}, keys = {list(block.keys())}")

        if block_type == "Text":
            if "res" in block and isinstance(block["res"], (list, tuple)):
                lines = [line[1][0] for line in block["res"] if isinstance(line, (list, tuple)) and len(line) > 1 and line[1]]
                text_content = "\n".join(lines).strip()
                if text_content:
                    markdown_blocks.append(text_content)

        elif block_type == "Title":
            if "res" in block and isinstance(block["res"], (list, tuple)):
                lines = [line[1][0] for line in block["res"] if isinstance(line, (list, tuple)) and len(line) > 1 and line[1]]
                title_text = "\n".join(lines).strip()
                if title_text:
                    markdown_blocks.append(f"# {title_text}")

        elif block_type == "Table":
            if "res" in block and isinstance(block["res"], dict) and "html" in block["res"]:
                html_table = block["res"]["html"]
                markdown_blocks.append(html_table)  # Embed HTML table (supported in most Markdown viewers)

        elif block_type in ["Figure", "Image", "Picture"]:
            markdown_blocks.append("\n![Figure / Image detected]\n")

        # Add handlers for other types if they appear (e.g., "Header", "List", "Equation")

    return "\n\n".join(markdown_blocks) if markdown_blocks else "(No content extracted from this page)"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Process all pages and build full Markdown document"""
    try:
        images = convert_pdf_to_images(pdf_bytes)

        if not images:
            return "(No pages found in PDF)"

        output = []

        for idx, img in enumerate(images, start=1):
            page_md = process_page(img)
            output.append(f"## Page {idx}\n\n{page_md}")

        full_md = "\n\n".join(output)
        return full_md if full_md.strip() else "(Empty document - check if PDF has selectable text or is heavily scanned)"

    except Exception as e:
        raise TextExtractionError(f"PaddleOCR PDF processing failed: {str(e)}") from e


def save_markdown(markdown_text: str, input_pdf_path: str) -> Path:
    """Save Markdown to file"""
    DUMP_DIR.mkdir(parents=True, exist_ok=True)

    input_name = Path(input_pdf_path).stem
    output_path = DUMP_DIR / f"{input_name}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python pdf_to_markdown_paddle_jp.py <input.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    try:
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        print("Processing PDF...\n")
        markdown_output = extract_text_from_pdf(pdf_content)

        print(markdown_output)
        print("\n" + "-"*60 + "\n")

        saved_path = save_markdown(markdown_output, pdf_path)
        print(f"Saved Markdown to: {saved_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)