"""Write a PDF of flashcards to print double-sided: photos on the front, names on the back."""

from pathlib import Path

from fpdf import FPDF

from members import Member

# US Letter, in inches. Cards are 2.5" squares, twelve to a sheet.
PAGE_WIDTH, PAGE_HEIGHT = 8.5, 11
COLUMNS, ROWS = 3, 4
CARD_SIZE = 2.5
LEFT_MARGIN = (PAGE_WIDTH - COLUMNS * CARD_SIZE) / 2
TOP_MARGIN = (PAGE_HEIGHT - ROWS * CARD_SIZE) / 2
PHOTO_PADDING = 0.15
NAME_FONT_SIZE = 18  # points
NAME_LINE_HEIGHT = 0.35


def write_printout(members: list[Member], path: Path) -> None:
    """Members without a photo are left out; a card with no face has nothing to quiz."""
    with_photos = [member for member in members if member.photo]
    pdf = FPDF(unit="in", format="letter")
    pdf.set_auto_page_break(False)
    pdf.set_font("Helvetica", "B", NAME_FONT_SIZE)
    pdf.set_draw_color(200)  # light gray cut lines

    per_sheet = COLUMNS * ROWS
    for start in range(0, len(with_photos), per_sheet):
        sheet = with_photos[start : start + per_sheet]
        pdf.add_page()
        for i, member in enumerate(sheet):
            x, y = card_corner(i, mirrored=False)
            pdf.rect(x, y, CARD_SIZE, CARD_SIZE)
            pdf.image(
                str(member.photo),
                x + PHOTO_PADDING,
                y + PHOTO_PADDING,
                w=CARD_SIZE - 2 * PHOTO_PADDING,
                h=CARD_SIZE - 2 * PHOTO_PADDING,
                keep_aspect_ratio=True,
            )
        pdf.add_page()
        for i, member in enumerate(sheet):
            x, y = card_corner(i, mirrored=True)
            write_name(pdf, member.name, x, y)

    pdf.output(str(path))


def card_corner(index: int, mirrored: bool) -> tuple[float, float]:
    """Top-left corner of a card. The back of a sheet is mirrored left-to-right, so each
    name lands behind its photo when printed double-sided (flip on long edge)."""
    row, column = divmod(index, COLUMNS)
    if mirrored:
        column = COLUMNS - 1 - column
    return LEFT_MARGIN + column * CARD_SIZE, TOP_MARGIN + row * CARD_SIZE


def write_name(pdf: FPDF, name: str, x: float, y: float) -> None:
    """Write the name centered in the card, wrapping long names."""
    # The PDF's built-in font only covers Latin-1; anything else prints as "?".
    name = name.encode("latin-1", "replace").decode("latin-1")
    width = CARD_SIZE - 2 * PHOTO_PADDING
    # Shrink the font for names with a word too long to fit, so no word is split.
    font_size = NAME_FONT_SIZE
    pdf.set_font_size(font_size)
    while max(pdf.get_string_width(word) for word in name.split()) > width:
        font_size -= 1
        pdf.set_font_size(font_size)
    lines =pdf.multi_cell(width, NAME_LINE_HEIGHT, name, dry_run=True, output="LINES")
    pdf.set_xy(x + PHOTO_PADDING, y + (CARD_SIZE - len(lines) * NAME_LINE_HEIGHT) / 2)
    pdf.multi_cell(width, NAME_LINE_HEIGHT, name, align="C")
