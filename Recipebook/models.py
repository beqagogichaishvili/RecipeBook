from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Recipe:
    _id: str
    title: str
    rating: int = 0
    last_watched: datetime = None
    ingredients: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    cook_method: str = None
    video_link: str = None


@dataclass
class User:
    _id: str
    email: str
    password: str
    recipes: list[str] = field(default_factory=list)

