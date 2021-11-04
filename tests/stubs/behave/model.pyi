from typing import Any
from typing import ClassVar
from typing import Iterable
from typing import Iterator
from typing import Literal
from typing import Protocol
from typing import Sequence

from .model_core import BasicStatement
from .model_core import Replayable
from .model_core import Status
from .model_core import TagAndStatusStatement
from .runner import ModelRunner
from .tag_expression import TagExpression

Configuration = dict[str, Any]


def reset_model(model_elements: Iterable[ModelElement]) -> None: ...


class ModelElement(Protocol):

	def reset(self) -> None: ...


class Feature(TagAndStatusStatement, Replayable):

	type: ClassVar[Literal["feature"]]

	keyword: str
	name: str
	description: list[str]
	background: Background
	scenarios: list[Scenario]
	tags: list[Tag]
	hook_failed: bool
	filename: str
	line: int
	language: str

	@property
	def status(self) -> Status: ...

	@property
	def duration(self) -> float: ...

	def __init__(
		self,
		filename: str,
		line: int,
		keyword: str,
		name: str,
		tags: Sequence[Tag] = ...,
		description: str = ...,
		scenarios: Sequence[Scenario] = ...,
		background: Background = ...,
		language: str = ...,
	): ...
	def __iter__(self) -> Iterator[Scenario]: ...

	def reset(self) -> None: ...
	def add_scenario(self, scenario: Scenario) -> None: ...
	def compute_status(self) -> Status: ...
	def walk_scenarios(self, with_outlines: bool = ...) -> list[Scenario]: ...
	def should_run(self, config: Configuration = ...) -> bool: ...
	def should_run_with_tags(self, tag_expression: TagExpression) -> bool: ...
	def mark_skipped(self) -> None: ...
	def skip(self, reason: str = ..., require_not_executed: bool = ...) -> None: ...
	def run(self, runner: ModelRunner) -> bool: ...


class Background(BasicStatement, Replayable):

	type: ClassVar[Literal["background"]]

	keyword: str
	name: str
	steps: list[Step]
	filename: str
	line: int

	@property
	def duration(self) -> float: ...

	def __init__(
		self,
		filename: str,
		line: int,
		keyword: str,
		name: str,
		steps: Sequence[Step] = ...,
	): ...
	def __iter__(self) -> Iterator[Step]: ...


class Scenario(TagAndStatusStatement, Replayable):

	type: ClassVar[Literal["scenario"]]
	continue_after_failed_step: ClassVar[bool]

	keyword: str
	name: str
	description: str
	feature: Feature
	steps: Sequence[Step]
	tags: Sequence[Tag]
	hook_failed: bool
	filename: str
	line: int

	@property
	def background_steps(self) -> list[Step]: ...

	@property
	def all_steps(self) -> Iterator[Step]: ...

	@property
	def duration(self) -> float: ...

	@property
	def effective_tags(self) -> list[Tag]: ...

	def __init__(
		self,
		filename: str,
		line: int,
		keyword: str,
		name: str,
		tags: Sequence[Tag] = ...,
		steps: Sequence[Step] = ...,
		description: str = ...,
	): ...
	def __iter__(self) -> Iterator[Step]: ...

	def reset(self) -> None: ...
	def compute_status(self) -> Status: ...
	def should_run(self, config: Configuration = ...) -> bool: ...
	def should_run_with_tags(self, tag_expression: TagExpression) -> bool: ...
	def should_run_with_name_select(self, config: Configuration) -> bool: ...
	def mark_skipped(self) -> None: ...
	def skip(self, reason: str = ..., require_not_executed: bool = ...) -> None: ...
	def run(self, runner: ModelRunner) -> bool: ...


class Step(BasicStatement, Replayable):

	type: ClassVar[Literal["step"]]

	keyword: str
	name: str
	step_type: str
	text: Text|None
	table: Table|None
	status: Status
	hook_failed: bool
	duration: float
	error_message: str|None
	filename: str
	line: int

	def __init__(
		self,
		filename: str,
		line: int,
		keyword: str,
		step_type: str,
		name: str,
		text: Text = ...,
		table: Table = ...,
	): ...
	def __eq__(self, other: Any) -> bool: ...
	def __hash__(self) -> int: ...

	def reset(self) -> None: ...
	def run(self, runner: ModelRunner, quiet: bool = ..., capture: bool = ...) -> bool: ...


class Table(Replayable):

	type: ClassVar[Literal["table"]]

	headings: Sequence[str]
	line: int|None
	rows: list[Row]

	def __init__(self, headings: Sequence[str], line: int = ..., rows: Sequence[Row] = ...): ...
	def __eq__(self, other: Any) -> bool: ...
	def __iter__(self) -> Iterator[Row]: ...
	def __getitem__(self, index: int) -> Row: ...

	def add_row(self, row: Sequence[str], line: int) -> None: ...
	def add_column(self, column_name: str, values: Iterable[str], default_value: str = ...) -> int: ...
	def remove_column(self, column_name: str) -> None: ...
	def remove_columns(self, column_names: Iterable[str]) -> None: ...
	def has_column(self, column_name: str) -> bool: ...
	def get_column_index(self, column_name: str) -> int: ...
	def require_column(self, column_name: str) -> int: ...
	def require_columns(self, column_names: Iterable[str]) -> None: ...
	def ensure_column_exists(self, column_name: str) -> int: ...
	def assert_equals(self, data: Table|Iterable[Row]) -> None: ...


class Row:

	headings: Sequence[str]
	cells: Sequence[str]
	line: int|None
	comments: Sequence[str]|None

	def __init__(
		self,
		headings: Sequence[str],
		cells: Sequence[str],
		line: int = ...,
		comments: Sequence[str] = ...,
	): ...
	def __getitem__(self, index: int) -> str: ...
	def __eq__(self, other: Any) -> bool: ...
	def __len__(self) -> int: ...
	def __iter__(self) -> Iterator[str]: ...

	def items(self) -> Iterator[tuple[str, str]]: ...
	def get(self, key: int, default: str = ...) -> str: ...
	def as_dict(self) -> dict[str, str]: ...


class Tag(str):

	allowed_chars: ClassVar[str]
	quoting_chars: ClassVar[str]

	line: int

	def __init__(self, name: str, line: int): ...

	@classmethod
	def make_name(cls, text: str, unexcape: bool = ..., allowed_chars: str = ...) -> str: ...


class Text(str):

	content_type: Literal["text/plain"]
	line: int

	def __init__(self, value: str, content_type: Literal["text/plain"] = ..., line: int = ...): ...

	def line_range(self) -> tuple[int, int]: ...
	def replace(self, old: str, new: str, count: int = ...) -> Text: ...
	def assert_equals(self, expected: str) -> bool: ...
