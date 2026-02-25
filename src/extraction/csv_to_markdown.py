import csv
import io
import os
from pathlib import Path

try:
    from charset_normalizer import from_bytes
except ImportError:
    from charset_normalizer import detect  # older API fallback


class TextExtractionError(Exception):
    pass


DUMP_DIR = Path("/Users/admin/LG/Markdown/data/dump")


def extract_text_from_csv(file_content: bytes) -> str:
    # Candidate encodings — ordered roughly by Japanese likelihood
    candidate_encodings = [
        None,               # let charset-normalizer decide first
        "utf-8-sig",
        "shift_jis",
        "cp932",
        "utf-8",
        "latin1",           # very last resort
    ]

    detected_encoding = None
    text = None

    for enc in candidate_encodings:
        try:
            if enc is None:
                result = from_bytes(file_content).best()
                if result:
                    detected_encoding = result.encoding
                    text = file_content.decode(detected_encoding, errors="replace")
            else:
                detected_encoding = enc
                text = file_content.decode(enc, errors="replace")

            if text is not None:
                break
        except (UnicodeDecodeError, LookupError):
            continue

    if text is None:
        raise TextExtractionError("Could not decode CSV with any supported encoding")

    try:
        csv_file = io.StringIO(text)
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)

        if not rows:
            return ""

        # Clean multi-line cells → single line
        clean = lambda cell: cell.replace("\n", " ").replace("\r", " ").strip()

        header = [clean(cell) for cell in rows[0]]
        md = "| " + " | ".join(header) + " |\n"
        md += "| " + " | ".join(["---"] * len(header)) + " |\n"

        for row in rows[1:]:
            cleaned_row = [clean(cell) for cell in row]
            md += "| " + " | ".join(cleaned_row) + " |\n"

        return md

    except Exception as e:
        raise TextExtractionError(
            f"CSV parsing failed (detected: {detected_encoding}): {str(e)}"
        ) from e


def save_markdown(markdown_text: str, input_csv_path: str):
    """
    Save generated markdown into dump directory
    """
    DUMP_DIR.mkdir(parents=True, exist_ok=True)

    input_name = Path(input_csv_path).stem
    output_path = DUMP_DIR / f"{input_name}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python csv_to_markdown_jp.py <input.csv>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path, "rb") as f:
            content = f.read()

        markdown_output = extract_text_from_csv(content)

        # Print to stdout (same behavior as before)
        print(markdown_output)

        # Save to dump directory
        saved_path = save_markdown(markdown_output, path)
        print(f"\nSaved Markdown to: {saved_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)