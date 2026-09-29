from dataclasses import dataclass
from typing import Optional


@dataclass
class Note:
    title: str
    category: str
    content: str
    id: Optional[int] = None