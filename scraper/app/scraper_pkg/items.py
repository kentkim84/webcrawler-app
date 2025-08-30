from dataclasses import dataclass


@dataclass
class PageItem:
    url: str
    title: str
    text: str
    normalized: dict