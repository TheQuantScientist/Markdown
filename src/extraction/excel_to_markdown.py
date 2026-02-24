# excel_to_markdown_jp.py
"""
Excel → Markdown tables (one per sheet) — works well for Japanese .xlsx files
"""
import io
import pandas as pd

class TextExtractionError(Exception):
    pass

def extract_text_from_excel(file_content: bytes) -> str:
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_content))
        output = []

        for sheet_name in excel_file.sheet_names:
            try:
                # For .xlsx → openpyxl is usually best (handles most encodings internally)
                # For very old .xls → may need xlrd + encoding tricks (rare nowadays)
                df = excel_file.parse(sheet_name=sheet_name, engine="openpyxl")

                if df.empty:
                    continue

                df = df.dropna(how="all")

                # Flatten multi-line cells and headers
                df = df.map(lambda x: " ".join(str(x).splitlines()).strip() if pd.notna(x) else x)
                df.columns = [" ".join(str(c).splitlines()).strip() for c in df.columns]

                # Build markdown table
                header = "| " + " | ".join(df.columns) + " |"
                sep    = "| " + " | ".join(["---"] * len(df.columns)) + " |"

                rows = ["| " + " | ".join(str(val) for val in row) + " |"
                        for row in df.itertuples(index=False)]

                table_md = "\n".join([header, sep] + rows)
                output.append(f"### Sheet: {sheet_name}\n\n{table_md}\n")

            except Exception as e:
                output.append(f"### Sheet: {sheet_name} — skipped (error: {str(e)})")

        if not output:
            return "(No readable sheets found)"

        return "\n\n".join(output)

    except Exception as e:
        raise TextExtractionError(f"Excel processing failed: {str(e)}") from e


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python excel_to_markdown_jp.py <input.xlsx>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "rb") as f:
            content = f.read()
        print(extract_text_from_excel(content))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)