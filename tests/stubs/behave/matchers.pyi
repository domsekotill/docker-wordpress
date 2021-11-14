from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Optional
from typing import Sequence
from typing import TypeVar

from parse import Parser
from parse import TypeConverter

from .model_core import Argument
from .model_core import FileLocation
from .runner import Context
from .step_registry import StepFunction

Arguments = Optional[list[Argument]]

T = TypeVar("T")


matcher_mapping: dict[str, Matcher]
current_matcher: Matcher


def register_type(**kw: Callable[[str], Any]) -> None: ...
def use_step_matcher(name: str) -> None: ...
def get_matcher(func: StepFunction, pattern: str) -> Matcher: ...


class StepParserError(ValueError): ...


class Match:

	func: StepFunction
	arguments: Sequence[Argument]|None
	location: int

	def __init__(self, func: StepFunction, arguments: Sequence[Argument] = ...): ...
	def with_arguments(self, arguments: Sequence[Argument]) -> Match: ...
	def run(self, context: Context) -> None: ...

	@staticmethod
	def make_location(step_function: StepFunction) -> FileLocation: ...


class NoMatch(Match):

	def __init__(self) -> None: ...


class MatchWithError(Match):

	def __init__(self, func: StepFunction, error: BaseException): ...


class Matcher:

	schema: ClassVar[str]

	pattern: str
	func: StepFunction

	def __init__(self, func: StepFunction, pattern: str, step_type: str = ...): ...

	@property
	def location(self) -> FileLocation: ...

	@property
	def regex_pattern(self) -> str: ...

	def describe(self, schema: str = ...) -> str: ...
	def check_match(self, step: str) -> Arguments: ...
	def match(self, step: StepFunction) -> Match: ...


class ParseMatcher(Matcher):

	custom_types: ClassVar[dict[str, TypeConverter[Any]]]
	parser_class: ClassVar[type[Parser]]


class CFParseMatcher(ParseMatcher): ...
class RegexMatcher(Matcher): ...
class SimplifiedRegexMatcher(RegexMatcher): ...
class CucumberRegexMatcher(RegexMatcher): ...
