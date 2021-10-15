#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Management and control for WordPress fixtures
"""

from __future__ import annotations

from contextlib import contextmanager
from subprocess import CalledProcessError
from time import sleep
from time import time
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Literal
from typing import SupportsBytes
from typing import TypeVar
from typing import overload

from .docker import Container
from .proc import PathArg
from .proc import coerce_args
from .proc import exec_io


def wait(predicate: Callable[[], bool], timeout: float = 120.0) -> None:
	"""
	Block and periodically call "predictate" until it returns True, or the time limit passes
	"""
	end = time() + timeout
	left = timeout
	while left > 0.0:
		sleep(
			10 if left > 60.0 else
			5 if left > 10.0 else
			1,
		)
		left = end - time()
		if predicate():
			return
	raise TimeoutError


class Cli:
	"""
	Manage calling executables in a container

	Any arguments passed to the constructor will prefix the arguments passed when the object
	is called.
	"""

	T = TypeVar("T")

	def __init__(self, container: Container, *cmd: PathArg):
		self.container = container
		self.cmd = cmd

	@overload
	def __call__(
		self,
		*args: PathArg,
		input: str|SupportsBytes|None = ...,
		deserialiser: Callable[[bytes], T],
		query: Literal[False],
		**kwargs: Any,
	) -> T: ...

	@overload
	def __call__(
		self,
		*args: PathArg,
		input: str|SupportsBytes|None = ...,
		deserialiser: None = None,
		query: Literal[True],
		**kwargs: Any,
	) -> int: ...

	@overload
	def __call__(
		self,
		*args: PathArg,
		input: str|SupportsBytes|None = ...,
		deserialiser: None = None,
		query: Literal[False],
		**kwargs: Any,
	) -> None: ...

	def __call__(
		self,
		*args: PathArg,
		input: str|SupportsBytes|None = None,
		deserialiser: Callable[[bytes], T]|None = None,
		query: bool = False,
		**kwargs: Any,
	) -> Any:
		# deserialiser = kwargs.pop('deserialiser', None)
		assert not deserialiser or not query

		data = (
			b"" if input is None else
			input.encode() if isinstance(input, str) else
			bytes(input)
		)
		cmd = self.container.get_exec_args([*self.cmd, *args], interactive=bool(data))

		if deserialiser:
			return exec_io(cmd, data, deserialiser=deserialiser, **kwargs)

		rcode = exec_io(cmd, data, **kwargs)
		if query:
			return rcode
		if not isinstance(rcode, int):
			raise TypeError(f"got rcode {rcode!r}")
		if 0 != rcode:
			raise CalledProcessError(rcode, ' '.join(coerce_args(cmd)))
		return None


class Wordpress(Container):
	"""
	Container subclass for a WordPress PHP-FPM container
	"""

	@property
	def cli(self) -> Cli:
		"""
		Run WP-CLI commands
		"""
		return Cli(self, "wp")

	@contextmanager
	def started(self) -> Iterator[Container]:
		with self:
			self.start()
			cmd = ["bash", "-c", "[[ /proc/1/exe -ef `which php-fpm` ]]"]
			wait(lambda: self.is_running() and self.run(cmd).returncode == 0, timeout=600)
			yield self


class Mysql(Container):
	"""
	Container subclass for a database container
	"""

	@property
	def mysql(self) -> Cli:
		"""
		Run "mysql" commands
		"""
		return Cli(self, "mysql")

	@property
	def mysqladmin(self) -> Cli:
		"""
		Run "mysqladmin" commands
		"""
		return Cli(self, "mysqladmin")

	@property
	def mysqldump(self) -> Cli:
		"""
		Run "mysqldump" commands
		"""
		return Cli(self, "mysqldump")

	@contextmanager
	def started(self) -> Iterator[Container]:
		with self:
			self.start()
			sleep(20)
			wait(lambda: self.run(['/healthcheck.sh']).returncode == 0)
			yield self
