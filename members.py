"""Scraped members, cached on disk so later runs resume instead of starting over."""

import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

DATA_DIR = Path("data")
HOUSEHOLDS_FILE = DATA_DIR / "households.json"
PHOTOS_DIR = DATA_DIR / "photos"
MAX_PHOTO_SIZE = 1024


@dataclass
class Member:
    name: str
    photo: Path | None = None


def load_households() -> dict[str, list[Member]]:
    """Return {household id: members} for every household scraped so far."""
    if not HOUSEHOLDS_FILE.is_file():
        return {}
    saved = json.loads(HOUSEHOLDS_FILE.read_text(encoding="utf-8"))
    return {
        household_id: [
            Member(m["name"], PHOTOS_DIR / m["photo"] if m["photo"] else None)
            for m in members
        ]
        for household_id, members in saved.items()
    }


def save_households(households: dict[str, list[Member]]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    saved = {
        household_id: [
            {"name": m.name, "photo": m.photo.name if m.photo else None}
            for m in members
        ]
        for household_id, members in households.items()
    }
    # Write then rename, so an interrupted run never leaves a half-written file.
    temp_file = HOUSEHOLDS_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(saved, indent=2), encoding="utf-8")
    temp_file.replace(HOUSEHOLDS_FILE)


def save_photo(name: str, photo: bytes) -> Path:
    """Save a photo as a JPEG no larger than MAX_PHOTO_SIZE and return its path."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    checksum = hashlib.sha1(photo).hexdigest()[:8]  # keeps people with the same name apart
    path = PHOTOS_DIR / f"{slug}_{checksum}.jpg"

    image = Image.open(io.BytesIO(photo)).convert("RGB")
    image.thumbnail((MAX_PHOTO_SIZE, MAX_PHOTO_SIZE))
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    image.save(path, format="JPEG", quality=85)
    return path
