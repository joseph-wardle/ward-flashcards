import hashlib
from pathlib import Path

import genanki

from member import Member
from member.image import get_image_as_file


def safe_filename(name: str) -> str:
    # Lowercase, remove non-alphanumeric characters except underscore
    safe = name.lower().replace(" ", "_")
    return safe


def hash_name_to_id(name: str) -> int:
    # Use SHA1 hash
    hash = hashlib.sha1(name.encode("utf-8")).hexdigest()
    # Take first 8 hex digits and convert to int
    return int(hash[:8], 16)  # 32-bit integer


def create_deck(deck_name: str, members: list[Member], filepath: Path):
    model_name = "Image-Name Model"

    deck_id = hash_name_to_id(deck_name)
    model_id = hash_name_to_id(model_name)

    # Create a new Anki deck
    deck = genanki.Deck(
        deck_id,  # unique deck id
        deck_name,
    )

    model = genanki.Model(
        model_id,
        "Image-Name Model",
        fields=[
            {"name": "Image"},
            {"name": "Name"},
        ],
        templates=[
            {
                "name": "Face -> Name",
                "qfmt": """
                <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                    <div style="text-align: center;">
                        <div style="
                            display: inline-block;
                            max-width: 250px;
                            max-height: 250px;
                            border-radius: 15px;
                            box-shadow: 0 0 10px rgba(0,0,0,0.2);
                            margin-bottom: 20px;
                            overflow: hidden;
                            background-color: var(--card-background);
                        ">
                            {{Image}}
                        </div>
                    </div>
                </div>
                """,
                "afmt": """
                <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                    <div style="text-align: center;">
                        <div style="
                            display: inline-block;
                            max-width: 250px;
                            max-height: 250px;
                            border-radius: 15px;
                            box-shadow: 0 0 10px rgba(0,0,0,0.2);
                            margin-bottom: 20px;
                            overflow: hidden;
                            background-color: var(--card-background);
                        ">
                            {{Image}}
                        </div>
                        <div style="
                            font-size: 32px;
                            font-weight: bold;
                            color: var(--text-color);
                            margin-top: 10px;
                        ">
                            {{Name}}
                        </div>
                    </div>
                </div>
                """,
            },
        ],
        sort_field_index=1,
    )

    # Download images and create notes
    media_files = []
    for member in members:
        if member.name == "":
            continue

        image_path = get_image_as_file(member)
        if image_path is not None:
            media_files.append(str(image_path))
            img_name = image_path.name
            image_field = f"<img src='{str(img_name)}'>"
        else:
            first_name = member.name.split(" ", 1)[0]
            last_name = member.name.rsplit(" ", 1)[-1]
            if member.gender is not None:
                image_field = f"No Image (Hint: {member.gender}, Name starts with {first_name[0]}, Last name is {last_name})."
            else:
                image_field = f"No Image (Hint: Name starts with {first_name[0]}, Last name is {last_name})."

        note = genanki.Note(model=model, fields=[image_field, member.name])
        deck.add_note(note)

    # Save deck
    print(f"Saving Deck: {deck_name} to {filepath}")
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(filepath)
