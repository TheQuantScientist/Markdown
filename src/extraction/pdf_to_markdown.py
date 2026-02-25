# pdf_to_markdown_docling.py
"""
PDF → Markdown using Docling (lightweight, efficient)

- Low memory usage (ideal for Mac M2)
- Good table extraction to Markdown tables
- Handles Japanese text in digital PDFs
- CPU-only, ready for Ubuntu server later

Install:
    pip install docling

Run:
    python pdf_to_markdown_docling.py /path/to/your.pdf
"""

from pathlib import Path
import sys
from datetime import datetime

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("Docling not installed. Install it with:")
    print("    pip install docling")
    sys.exit(1)

# ================================================
# CONFIG
# ================================================

OUTPUT_DIR = Path("/Users/admin/LG/Markdown/data/dump")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Optional: limit pages to avoid memory issues (None = all pages)
MAX_PAGES = None  # e.g. set to 10 for testing large PDFs

# ================================================

def pdf_to_markdown(pdf_path: str | Path) -> str:
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    print(f"Converting: {pdf_path.name}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        converter = DocumentConverter()

        # Convert without extra kwargs (API expects only source)
        result = converter.convert(pdf_path)

        # Optional page limit (rough slice after conversion)
        if MAX_PAGES is not None:
            # Docling doesn't paginate perfectly, but we can approximate
            md_full = result.document.export_to_markdown()
            # Split by common page markers or headings; adjust as needed
            blocks = md_full.split("\n\n")  # rough block split
            limited_blocks = blocks[:MAX_PAGES * 3]  # conservative
            md_content = "\n\n".join(limited_blocks)
        else:
            md_content = result.document.export_to_markdown()

        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return md_content

    except Exception as e:
        raise RuntimeError(f"Docling conversion failed: {str(e)}") from e


def save_markdown(md_content: str, pdf_path: str | Path) -> Path:
    pdf_path = Path(pdf_path)
    stem = pdf_path.stem
    out_path = OUTPUT_DIR / f"{stem}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("    python pdf_to_markdown_docling.py <input.pdf>")
        print("")
        print("Example:")
        print("    python pdf_to_markdown_docling.py /Users/admin/LG/Markdown/data/pdf/20253rd_financialresult_059_e.pdf")
        sys.exit(1)

    input_pdf = sys.argv[1]

    try:
        markdown_text = pdf_to_markdown(input_pdf)

        # Show preview
        preview_length = 1800
        preview = markdown_text[:preview_length]
        if len(markdown_text) > preview_length:
            preview += "\n\n... (truncated - see full file for complete output)"

        print("\n" + "="*70)
        print("Markdown Preview (first part):")
        print("-"*70)
        print(preview)
        print("="*70 + "\n")

        saved_path = save_markdown(markdown_text, input_pdf)
        print(f"Markdown successfully saved to:")
        print(f"  {saved_path}")

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)