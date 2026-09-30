"""Branded PDF generation with page-safe text wrapping."""

from io import BytesIO
import re

from fpdf import FPDF

from .document_formatter import LOGO
from .text_utils import parse_document


def _pdf_safe(text: str) -> str:
    """Encode core-font text and add break opportunities in unusually long tokens."""
    encoded = text.encode("cp1252", "replace").decode("cp1252")
    return re.sub(r"\S{31,}", lambda match: " ".join(
        match.group()[index:index + 30]
        for index in range(0, len(match.group()), 30)
    ), encoded)


class _LegalEasePDF(FPDF):
    def header(self) -> None:
        if LOGO.is_file():
            self.image(str(LOGO), x=10, y=8, w=34)
        else:
            self.set_font("Times", "B", 10)
            self.set_text_color(36, 83, 110)
            self.cell(0, 8, "LegalEase", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(190, 203, 213)
        self.line(15, 23, 195, 23)
        self.set_y(29)

    def footer(self) -> None:
        self.set_y(-17)
        self.set_draw_color(190, 203, 213)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_y(-14)
        self.set_font("Times", "I", 8)
        self.set_text_color(90, 100, 110)
        self.cell(0, 8, f"LegalEase | AI-generated draft     Page {self.page_no()}", align="C")


def format_pdf(text: str, doc_type: str = "Legal Document") -> bytes:
    pdf = _LegalEasePDF()
    # Core fonts use Windows-1252 for legal punctuation such as curly quotes and bullets.
    pdf.core_fonts_encoding = "cp1252"
    pdf.set_margins(20, 31, 20)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_page()
    blocks = parse_document(text)
    first_title = next((content for kind, content in blocks if kind == "title"), doc_type)
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(27, 56, 78)
    pdf.multi_cell(0, 8, _pdf_safe(first_title), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for kind, content in blocks:
        if kind == "blank":
            pdf.ln(3)
        elif kind == "title":
            continue
        elif kind == "heading2":
            pdf.ln(2)
            pdf.set_font("Times", "B", 12)
            pdf.set_text_color(27, 56, 78)
            pdf.multi_cell(0, 7, _pdf_safe(content), new_x="LMARGIN", new_y="NEXT")
        elif kind == "list":
            pdf.set_font("Times", "", 11)
            pdf.multi_cell(0, 6, f"    -  {_pdf_safe(content)}", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Times", "", 11)
            pdf.set_text_color(25, 25, 25)
            pdf.multi_cell(0, 6, _pdf_safe(content), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
    return bytes(pdf.output())
