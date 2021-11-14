import contextlib
from io import StringIO
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Literal
from typing import Protocol
from typing import Sequence
from typing import Union

from .capture import CaptureController
from .formatter.base import Formatter
from .log_capture import LoggingCapture
from .model import Configuration
from .model import Feature
from .model import Row
from .model import Scenario
from .model import Step
from .model import Table
from .model import Tag
from .model_core import FileLocation
from .step_registry import StepRegistry

Mode = Union[Literal["behave"], Literal["user"]]


@contextlib.contextmanager
def use_context_with_mode(context: Context, mode: Mode) -> Iterator[None]: ...

@contextlib.contextmanager
def scoped_context_layer(context: Context, layer_name: str|None = None) -> Iterator[Context]: ...

def path_getrootdir(path: str)-> str: ...


class CleanupError(RuntimeError): ...
class ContextMaskWarning(UserWarning): ...


class Context(Protocol):

	def __getattr__(self, name: str) -> Any: ...
	def __setattr__(self, name: str, value: Any) -> None: ...
	def __contains__(self, name: str) -> bool: ...

	def add_cleanup(self, cleanup_func: Callable[..., None], *a: Any, **k: Any) -> None: ...

	@property
	def config(self) -> Configuration: ...

	@property
	def aborted(self) -> bool: ...

	@property
	def failed(self) -> bool: ...

	@property
	def log_capture(self) -> LoggingCapture|None: ...

	@property
	def stdout_capture(self) -> StringIO|None: ...

	@property
	def stderr_capture(self) -> StringIO|None: ...

	@property
	def cleanup_errors(self) -> int: ...

	# Feature always present, None outside of feature namespace

	@property
	def feature(self) -> Feature|None: ...

	# Step values always present, may be None even in step namespace

	@property
	def active_outline(self) -> Row|None: ...

	@property
	def table(self) -> Table|None: ...

	@property
	def text(self) -> str|None: ...


class FeatureContext(Protocol, Context):

	def execute_steps(self, steps_text: str) -> bool: ...

	@property
	def feature(self) -> Feature: ...

	@property
	def tags(self) -> set[Tag]: ...


class ScenarioContext(Protocol, FeatureContext):

	@property
	def scenario(self) -> Scenario: ...


class Hook(Protocol):

	def __call__(self, context: Context, *args: Any) -> None: ...


class ModelRunner:

	config: Configuration
	features: Sequence[Feature]
	step_registry: StepRegistry
	hooks: dict[str, Hook]
	formatters: list[Formatter]
	undefined_steps: list[Step]
	capture_controller: CaptureController
	context: Context|None
	feature: Feature|None
	hook_failures: int

	# is a property in concrete class
	aborted: bool

	def __init__(
		self,
		config: Configuration,
		features: Sequence[Feature]|None,
		step_registry: StepRegistry|None,
	): ...

	def run_hook(self, name: str, context: Context, *args: Any) -> None: ...
	def setup_capture(self) -> None: ...
	def start_capture(self) -> None: ...
	def stop_capture(self) -> None: ...
	def teardown_capture(self) -> None: ...
	def run_model(self, features: Sequence[Feature]|None) -> bool: ...
	def run(self) -> bool: ...


class Runner(ModelRunner):

	def __init__(self, config: Configuration): ...
	def setup_paths(self) -> None: ...
	def before_all_default_hook(self, context: Context) -> None: ...
	def load_hooks(self, filename: str = ...) -> None: ...
	def load_step_definitions(self, extra_step_paths: Sequence[str] = ...) -> None: ...
	def feature_locations(self) -> list[FileLocation]: ...
	def run_with_paths(self) -> bool: ...
