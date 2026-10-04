from dataclasses import dataclass


@dataclass
class Member:
    name: str
    image_url: str | None = None
    image_data: bytes | None = None
    gender: str | None = None

    def __str__(self) -> str:
        return f"{self.name}"
