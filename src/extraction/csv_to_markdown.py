# csv_to_markdown_jp.py
"""
CSV → Markdown table converter with strong Japanese encoding support
"""
import csv
import io
try:
    from charset_normalizer import from_bytes
except ImportError:
    from charset_normalizer import detect  # older API fallback

class TextExtractionError(Exception):
    pass

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
                # Use charset-normalizer (best for Japanese mixed content)
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
        md += "| " + " | ".join(["---"] * len(header)) + " |\n"   # simpler separator

        for row in rows[1:]:
            cleaned_row = [clean(cell) for cell in row]
            md += "| " + " | ".join(cleaned_row) + " |\n"

        return md

    except Exception as e:
        raise TextExtractionError(f"CSV parsing failed (detected: {detected_encoding}): {str(e)}") from e


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python csv_to_markdown_jp.py <input.csv>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "rb") as f:
            content = f.read()
        print(extract_text_from_csv(content))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)