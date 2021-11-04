import sys
from typing import Any
from typing import Iterator
from typing import Protocol
from typing import TypeVar
from typing import overload

from .runner import Context

C = TypeVar("C", bound=Context)
C_con = TypeVar("C_con", bound=Context, contravariant=True)

R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)


# There's a lot of @overload-ed functions here as fixtures come in two varieties:
# 1) A @contextlib.contextmanager-like generator that yields an arbitrary object once.
# 2) A simple function that returns an arbitrary object
#
# "use_fixture" allows both types of fixture callables to be used in the same way

if sys.version_info >= (3, 10) and False:
	# This depends on complete support of ParamSpec in mypy so is disabled for now.

	from typing import ParamSpec

	P = ParamSpec("P")


	class FixtureCoroutine(Protocol[C_con, P, R_co]):
		def __call__(self, _: C_con, /, *__a: P.args, **__k: P.kwargs) -> Iterator[R_co]: ...

	class FixtureFunction(Protocol[C_con, P, R_co]):
		def __call__(self, _: C_con, /, *__a: P.args, **__k: P.kwargs) -> R_co: ...


	@overload
	def use_fixture(
		fixture_func: FixtureCoroutine[C_con, P, R],
		context: C_con,
		*a: P.args,
		**k: P.kwargs,
	) -> R: ...

	@overload
	def use_fixture(
		fixture_func: FixtureFunction[C_con, P, R],
		context: C_con,
		*a: P.args,
		**k: P.kwargs,
	) -> R: ...

else:
	# Without ParamSpec no checking is done to ensure the arguments passed to use_fixture
	# match the fixture's arguments; fixtures must be able to handle arguments not being
	# supplied (except the context); and fixtures must accept ANY arbitrary keyword
	# arguments.

	P = TypeVar("P", bound=None)
	P_co = TypeVar("P_co", covariant=True)  # unused


	class FixtureCoroutine(Protocol[C_con, P_co, R_co]):
		def __call__(self, _: C_con, /, *__a: Any, **__k: Any) -> Iterator[R_co]: ...

	class FixtureFunction(Protocol[C_con, P_co, R_co]):
		def __call__(self, _: C_con, /, *__a: Any, **__k: Any) -> R_co: ...


	@overload
	def use_fixture(
		fixture_func: FixtureCoroutine[C_con, P_co, R_co],
		context: C_con,
		*a: Any,
		**k: Any,
	) -> R_co: ...

	@overload
	def use_fixture(
		fixture_func: FixtureFunction[C_con, P_co, R_co],
		context: C_con,
		*a: Any,
		**k: Any,
	) -> R_co: ...


# "fixture" is a decorator used to mark both types of fixture callables. It can also return
# a decorator, when called without the "func" argument.

@overload
def fixture(
	func: FixtureCoroutine[C, P, R],
	name: str = ...,
	pattern: str = ...,
) -> FixtureCoroutine[C, P, R]: ...

@overload
def fixture(
	func: FixtureFunction[C, P, R],
	name: str = ...,
	pattern: str = ...,
) -> FixtureFunction[C, P, R]: ...

@overload
def fixture(
	name: str = ...,
	pattern: str = ...,
) -> FixtureDecorator: ...


class FixtureDecorator(Protocol):

	@overload
	def __call__(self, _: FixtureCoroutine[C, P, R], /) -> FixtureCoroutine[C, P, R]: ...

	@overload
	def __call__(self, _: FixtureFunction[C, P, R], /) -> FixtureFunction[C, P, R]: ...
