from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class SearchOptions:
    only_search_title: bool
    category: str


@dataclass
class SearchResult:
    provider: str
    title: str
    url: str


@dataclass
class DetailItem:
    image: str
    description: str


@dataclass
class Detail:
    provider: str
    title: str
    url: str
    date: Optional[str] = None
    price: Optional[int] = None
    status: Optional[Union[str, None]] = None
    items: List[DetailItem] = None
