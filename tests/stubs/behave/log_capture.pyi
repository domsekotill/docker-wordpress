from logging import Handler
from logging import LogRecord
from logging.handlers import BufferingHandler
from typing import Any
from typing import Callable
from typing import Protocol
from typing import TypeVar
from typing import overload

from .model import Configuration
from .runner import ScenarioContext

class RecordFilter:

	include: set[str]
	exclude: set[str]

	def __init__(self, names: str): ...

	def filter(self, record: LogRecord) -> bool: ...


class LoggingCapture(BufferingHandler):

	config: Configuration
	old_handlers: list[Handler]
	old_level: int|None

	def __init__(self, config: Configuration, level: int = ...): ...

	def flush(self) -> None: ...
	def truncate(self) -> None: ...
	def getvalue(self) -> str: ...
	def find_event(self, pattern: str) -> bool: ...
	def any_errors(self) -> bool: ...
	def inveigle(self) -> None: ...
	def abandon(self) -> None: ...


MemoryHandler = LoggingCapture


class Hook(Protocol):
	def __call__(self, _: ScenarioContext, /, *a: Any, **k: Any) -> None: ...


H = TypeVar("H", bound=Hook)


@overload
def capture(level: int = ...) -> Callable[[H], H]: ...


@overload
def capture(func: H, level: int = ...) -> H: ...
