"""Generate PDF report from docs/report.md"""

import argparse
import os
import re


def _reshape_arabic(text: str) -> str:
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        return get_display(arabic_reshaper.reshape(text))
    except ImportError:
        return text


def _find_font() -> str | None:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    for name in ("arial.ttf", "tahoma.ttf"):
        path = os.path.join(windir, "Fonts", name)
        if os.path.exists(path):
            return path
    return None


def _safe_text(text: str) -> str:
    text = text.replace("\t", " ").strip()
    if len(text) > 400:
        text = text[:397] + "..."
    return text or "-"


def _write_line(pdf, text: str, height: float = 6.0, font_size: int = 11) -> None:
    pdf.set_font_size(font_size)
    pdf.set_x(pdf.l_margin)
    try:
        pdf.multi_cell(pdf.epw, height, _reshape_arabic(text))
    except Exception:
        ascii_text = text.encode("ascii", errors="ignore").decode("ascii")
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, height, ascii_text or "-")


def markdown_to_pdf(md_path: str, pdf_path: str) -> str:
    from fpdf import FPDF

    with open(md_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = _find_font()
    if font_path:
        pdf.add_font("BodyFont", "", font_path)
        pdf.set_font("BodyFont", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            pdf.ln(3)
            continue

        if line.startswith("# "):
            _write_line(pdf, line[2:].strip(), height=8, font_size=16)
            continue

        if line.startswith("## "):
            _write_line(pdf, line[3:].strip(), height=7, font_size=13)
            continue

        if line.startswith("### "):
            _write_line(pdf, line[4:].strip(), height=6, font_size=12)
            continue

        if line.startswith("```") or line.strip() == "---":
            continue

        clean = _safe_text(line)
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", clean)
        clean = re.sub(r"`(.+?)`", r"\1", clean)
        clean = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", clean)
        _write_line(pdf, clean)

    os.makedirs(os.path.dirname(pdf_path) or ".", exist_ok=True)
    pdf.output(pdf_path)
    return pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PDF from markdown report")
    parser.add_argument("--input", type=str, default="docs/report.md")
    parser.add_argument("--output", type=str, default="docs/report.pdf")
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = args.input if os.path.isabs(args.input) else os.path.join(root, args.input)
    pdf_path = args.output if os.path.isabs(args.output) else os.path.join(root, args.output)

    if not os.path.exists(md_path):
        raise SystemExit(f"Report not found: {md_path}")

    try:
        import fpdf  # noqa: F401
    except ImportError:
        raise SystemExit("Install fpdf2: pip install fpdf2 arabic-reshaper python-bidi")

    out = markdown_to_pdf(md_path, pdf_path)
    print(f"PDF saved: {out}")


if __name__ == "__main__":
    main()
