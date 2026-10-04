"""Write an Anki deck with one "photo -> name" card per member."""

import hashlib
import html
from pathlib import Path

import genanki

from members import Member


def stable_id(name: str) -> int:
    """Anki identifies decks and note types by number; derive one that never changes."""
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:8], 16)


CARD_STYLE = """
.center { display: flex; justify-content: center; align-items: center; height: 100%; }
.center > div { text-align: center; }
.photo {
    display: inline-block;
    max-width: 250px;
    max-height: 250px;
    border-radius: 15px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    margin-bottom: 20px;
    overflow: hidden;
    background-color: var(--card-background);
}
.name { font-size: 32px; font-weight: bold; color: var(--text-color); margin-top: 10px; }
"""

# The note type's name and field names stay the same as earlier versions, so decks
# built now update previously imported ones instead of duplicating the note type.
CARD_MODEL = genanki.Model(
    stable_id("Image-Name Model"),
    "Image-Name Model",
    fields=[{"name": "Image"}, {"name": "Name"}],
    templates=[
        {
            "name": "Face -> Name",
            "qfmt": '<div class="center"><div>'
            '<div class="photo">{{Image}}</div>'
            "</div></div>",
            "afmt": '<div class="center"><div>'
            '<div class="photo">{{Image}}</div>'
            '<div class="name">{{Name}}</div>'
            "</div></div>",
        }
    ],
    css=CARD_STYLE,
    sort_field_index=1,
)


def write_deck(deck_name: str, members: list[Member], path: Path) -> None:
    deck = genanki.Deck(stable_id(deck_name), deck_name)
    for member in members:
        fields = [front_of_card(member), html.escape(member.name)]
        deck.add_note(genanki.Note(model=CARD_MODEL, fields=fields))

    photos = [str(member.photo) for member in members if member.photo]
    genanki.Package(deck, media_files=photos).write_to_file(path)


def front_of_card(member: Member) -> str:
    if member.photo:
        return f'<img src="{member.photo.name}">'
    first_initial = member.name[0]
    last_name = member.name.rsplit(" ", 1)[-1]
    return html.escape(
        f"No photo (hint: first name starts with {first_initial}, last name is {last_name})"
    )
