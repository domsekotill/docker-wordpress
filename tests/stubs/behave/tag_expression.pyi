from typing import Iterable
from typing import Sequence

from .model import Tag

class TagExpression:

	ands: list[tuple[str]]
	limits: dict[tuple[str], int]

	def __init__(self, tag_expressions: Iterable[str]): ...
	def __len__(self) -> int: ...

	def check(self, tags: Sequence[Tag]) -> bool: ...

	@staticmethod
	def normalize_tag(tag: str) -> str: ...

	@classmethod
	def normalized_tags_from_or(cls, expr: str) -> Iterable[str]: ...

	def store_and_extract_limits(self, tags: Iterable[str]) -> None: ...
