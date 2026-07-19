from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd

from library.utils import author_sort_key


READ_NOT_OWNED = "Read - Not Owned"


def _clean(value, fallback=""):
  text = str(value).strip()
  return fallback if not text or text.lower() in {"nan", "none"} else text


def _shelf_group(book):
  if _clean(book.get("Reading Status", "")) == READ_NOT_OWNED:
    return READ_NOT_OWNED
  return _clean(book.get("Genre", ""), "Uncategorized")


def _print_order(books, manual_orders):
  frames = []
  room_values = books.get("Room", pd.Series("Unknown", index=books.index))
  rooms = sorted(room_values.replace("", "Unknown").fillna("Unknown").unique())

  for room in rooms:
    if room in manual_orders:
      ordered = manual_orders[room].copy()
    else:
      ordered = books[room_values.replace("", "Unknown").fillna("Unknown") == room].copy()
      ordered["Shelf"] = ordered.apply(_shelf_group, axis=1)
      ordered["Author Sort"] = ordered["Author"].apply(author_sort_key)
      ordered = ordered.sort_values(["Shelf", "Author Sort", "Title"])
      ordered["Position"] = ordered.groupby("Shelf").cumcount() + 1

    ordered["Print Room"] = room
    frames.append(ordered)

  return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def build_library_pdf(books, manual_orders=None, library_name="Home Library"):
  """Return a compact, two-column PDF of the complete library as bytes."""
  from reportlab.lib.colors import HexColor
  from reportlab.lib.enums import TA_CENTER
  from reportlab.lib.pagesizes import letter
  from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
  from reportlab.lib.units import inch
  from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer

  manual_orders = manual_orders or {}
  ordered = _print_order(books, manual_orders)
  output = BytesIO()
  doc = BaseDocTemplate(
    output,
    pagesize=letter,
    leftMargin=0.38 * inch,
    rightMargin=0.38 * inch,
    topMargin=0.48 * inch,
    bottomMargin=0.42 * inch,
    title=library_name
  )

  gap = 0.22 * inch
  column_width = (doc.width - gap) / 2
  frames = [
    Frame(doc.leftMargin, doc.bottomMargin, column_width, doc.height, id="left"),
    Frame(doc.leftMargin + column_width + gap, doc.bottomMargin, column_width, doc.height, id="right")
  ]

  def page_number(canvas, current_doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(HexColor("#666666"))
    canvas.drawCentredString(letter[0] / 2, 0.2 * inch, f"Page {current_doc.page}")
    canvas.restoreState()

  doc.addPageTemplates(PageTemplate(id="catalog", frames=frames, onPage=page_number))
  styles = getSampleStyleSheet()
  title_style = ParagraphStyle(
    "CatalogTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=15, leading=17, alignment=TA_CENTER, spaceAfter=7
  )
  room_style = ParagraphStyle(
    "Room", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=10, leading=12, textColor=HexColor("#17365D"),
    spaceBefore=5, spaceAfter=2, keepWithNext=True
  )
  shelf_style = ParagraphStyle(
    "Shelf", parent=styles["Heading3"], fontName="Helvetica-Bold",
    fontSize=8.5, leading=10, textColor=HexColor("#555555"),
    spaceBefore=3, spaceAfter=1, keepWithNext=True
  )
  book_style = ParagraphStyle(
    "Book", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=7.2, leading=8.7, leftIndent=5, spaceAfter=1
  )

  story = [Paragraph(escape(library_name), title_style)]
  if ordered.empty:
    story.append(Paragraph("No books in the library.", book_style))
  else:
    for room, room_books in ordered.groupby("Print Room", sort=False):
      story.append(Paragraph(f"{escape(_clean(room, 'Unknown'))} ({len(room_books)})", room_style))
      for shelf, shelf_books in room_books.groupby("Shelf", sort=False):
        story.append(Paragraph(escape(_clean(shelf, "Uncategorized")), shelf_style))
        for _, book in shelf_books.sort_values("Position").iterrows():
          title = escape(_clean(book.get("Title", ""), "Untitled"))
          author = escape(_clean(book.get("Author", ""), "Unknown author"))
          story.append(Paragraph(f"<b>{title}</b> - {author}", book_style))
      story.append(Spacer(1, 3))

  doc.build(story)
  return output.getvalue()
