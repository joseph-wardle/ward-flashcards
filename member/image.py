import io
from pathlib import Path

import requests
from PIL import Image

from member.core import Member


def safe_filename(name: str) -> str:
    # Lowercase, remove non-alphanumeric characters except underscore
    safe = name.lower().replace(" ", "_")
    return safe


def _get_image_filepath(member: Member) -> Path:
    img_name = Path(safe_filename(member.name)).with_suffix(".jpg")
    img_path = Path("images") / img_name
    return img_path


def save_image(filepath: Path, data: bytes, max_size: int = 1024):
    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True)

    img = Image.open(io.BytesIO(data))
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img.save(filepath, format="JPEG", quality=80)
    else:
        with open(filepath, "wb") as f:
            f.write(data)


def get_image_as_file(member: Member) -> Path | None:
    if member.image_data is None and member.image_url is None:
        return None
    img_path = _get_image_filepath(member)
    if not img_path.is_file():
        if member.image_data is not None:
            save_image(img_path, member.image_data)
        if member.image_url:
            if not img_path.is_file():
                img_data = requests.get(member.image_url).content
                save_image(img_path, img_data)

    return img_path
