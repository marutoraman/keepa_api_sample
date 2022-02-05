from typing import Optional, List
from dataclasses import dataclass


@dataclass
class KeepaProduct:
    title: str
    asin: str
    description: Optional[str] = None
    price: Optional[int] = None
    thumbnail_urls: Optional[List] = None
    jan: Optional[List] = None
    url: Optional[str] = None
    
    def to_dict(self):
        return self.__dict__.copy()