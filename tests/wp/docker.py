#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Commands for managing Docker for fixtures
"""

from __future__ import annotations

import ipaddress
import json
from contextlib import contextmanager
from pathlib import Path
from secrets import token_hex
from subprocess import DEVNULL
from subprocess import PIPE
from subprocess import CompletedProcess
from subprocess import Popen
from subprocess import run
from types import TracebackType
from typing import IO
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import overload

from jsonpath import JSONPath

from .proc import Arguments
from .proc import Environ
from .proc import MutableArguments
from .proc import PathArg
from .proc import PathLike
from .proc import coerce_args

T_co = TypeVar('T_co', covariant=True)

HostMount = tuple[PathLike, PathLike]
NamedMount = tuple[str, PathLike]
AnonMount = PathLike
Mount = Union[HostMount, NamedMount, AnonMount]
Volumes = Iterable[Mount]

DOCKER = 'docker'


def docker(*args: PathArg, **env: str) -> None:
	"""
	Run a Docker command, with output going to stdout
	"""
	run([DOCKER, *coerce_args(args)], env=env, check=True)


def docker_output(*args: PathArg, **env: str) -> str:
	"""
	Run a Docker command, capturing and returning its stdout
	"""
	proc = run([DOCKER, *coerce_args(args)], env=env, check=True, stdout=PIPE, text=True)
	return proc.stdout.strip()


def docker_quiet(*args: PathArg, **env: str) -> None:
	"""
	Run a Docker command, directing its stdout to /dev/null
	"""
	run([DOCKER, *coerce_args(args)], env=env, check=True, stdout=DEVNULL)


class IPv4Address(ipaddress.IPv4Address):
	"""
	Subclass of IPv4Address that handle's docker idiosyncratic tendency to add a mask suffix
	"""

	T = TypeVar("T", bound="IPv4Address")

	@classmethod
	def with_suffix(cls: type[T], address: str) -> T:
		"""
		Construct an instance with a suffixed bitmask size
		"""
		address, *_ = address.partition("/")
		return cls(address)


class Item:
	"""
	A mix-in for Docker items that can be inspected
	"""

	T = TypeVar('T', bound=object)
	C = TypeVar('C', bound=object)

	_data: Optional[dict[str, Any]] = None

	def __init__(self, name: str):
		self.name = name
		self._data: Any = None

	def get_id(self) -> str:
		"""
		Return an identifier for the Docker item
		"""
		return self.name

	@overload
	def inspect(self, path: str, kind: type[T], convert: None = None) -> T: ...

	@overload
	def inspect(self, path: str, kind: type[T], convert: Callable[[T], C]) -> C: ...

	def inspect(self, path: str, kind: type[T], convert: Callable[[T], C]|None = None) -> T|C:
		"""
		Extract a value from an item's information by JSON path

		"kind" is the type of the extracted value, while "convert" is an optional callable
		that can turn that type to another type.  The return type will be the return type of
		"convert" if provided, "kind" otherwise.
		"""
		if self._data is None:
			with Popen([DOCKER, 'inspect', self.get_id()], stdout=PIPE) as proc:
				assert proc.stdout is not None
				results = json.load(proc.stdout)
			assert isinstance(results, list)
			assert len(results) == 1 and isinstance(results[0], dict)
			self._data = results[0]
		result = JSONPath(path).parse(self._data)
		if "*" not in path:
			try:
				result = result[0]
			except IndexError:
				raise KeyError(path) from None
		if not isinstance(result, kind):
			raise TypeError(f"{path} is wrong type; expected {kind}; got {type(result)}")
		if convert is None:
			return result
		return convert(result)


class Image(Item):
	"""
	Docker image items
	"""

	T = TypeVar('T', bound='Image')

	def __init__(self, iid: str):
		self.iid = iid

	@classmethod
	def build(cls: type[T], context: Path, target: str = "", **build_args: str) -> T:
		"""
		Build an image from the given context
		"""
		cmd: Arguments = [
			'build', context, f"--target={target}",
			*(f"--build-arg={arg}={val}" for arg, val in build_args.items()),
		]
		docker(*cmd, DOCKER_BUILDKIT='1')
		iid = docker_output(*cmd, '-q', DOCKER_BUILDKIT='1')
		return cls(iid)

	@classmethod
	def pull(cls: type[T], repository: str) -> T:
		"""
		Pull an image from a registry
		"""
		docker('pull', repository)
		iid = Item(repository).inspect('$.Id', str)
		return cls(iid)

	def get_id(self) -> str:
		return self.iid


class Container(Item):
	"""
	Docker container items

	Instances can be used as context managers that ensure the container is stopped on
	exiting the context.
	"""

	DEFAULT_ALIASES = tuple[str]()

	def __init__(
		self,
		image: Image,
		cmd: Arguments = [],
		volumes: Volumes = [],
		env: Environ = {},
		network: Network|None = None,
		entrypoint: HostMount|PathArg|None = None,
	):
		if isinstance(entrypoint, tuple):
			volumes = [*volumes, entrypoint]
			entrypoint = entrypoint[1]

		self.image = image
		self.cmd = cmd
		self.volumes = volumes
		self.env = env
		self.entrypoint = entrypoint
		self.networks = dict[Network, Tuple[str, ...]]()
		self._id: str|None = None

		if network:
			self.networks[network] = Container.DEFAULT_ALIASES

	def __enter__(self) -> Container:
		return self

	def __exit__(self, etype: type[BaseException], exc: BaseException, tb: TracebackType) -> None:
		if self._id and exc:
			self.show_logs()
		self.stop(rm=True)

	@contextmanager
	def started(self) -> Iterator[Container]:
		"""
		A context manager that ensures the container is started when the context is entered
		"""
		with self:
			self.start()
			yield self

	def is_running(self) -> bool:
		"""
		Return whether the container is running
		"""
		if self._id is None:
			return False
		item = Item(self._id)
		if item.inspect('$.State.Status', str) == 'exited':
			code = item.inspect('$.State.ExitCode', int)
			raise ProcessLookupError(f"container {self._id} exited ({code})")
		return (
			self._id is not None
			and item.inspect('$.State.Running', bool)
		)

	def get_id(self) -> str:
		if self._id is not None:
			return self._id

		networks = set[Network]()
		opts: MutableArguments = [
			*(
				(f"--volume={vol[0]}:{vol[1]}" if isinstance(vol, tuple) else f"--volume={vol}")
				for vol in self.volumes
			),
			*(f"--env={name}={val}" for name, val in self.env.items()),
		]

		if self.entrypoint:
			opts.append(f"--entrypoint={self.entrypoint}")
		if self.networks:
			networks.update(self.networks)
			net = networks.pop()
			opts.append(f"--network={net}")
			opts.extend(f"--network-alias={alias}" for alias in self.networks[net])

		self._id = docker_output('container', 'create', *opts, self.image.iid, *self.cmd)
		assert self._id
		return self._id

	def start(self) -> None:
		"""
		Start the container
		"""
		docker_quiet('container', 'start', self.get_id())

	def stop(self, rm: bool = False) -> None:
		"""
		Stop the container
		"""
		if self._id is None:
			return
		docker_quiet('container', 'stop', self._id)
		if rm:
			docker_quiet('container', 'rm', self._id)
			self._id = None

	def connect(self, network: Network, *aliases: str) -> None:
		"""
		Connect the container to a Docker network

		Any aliases supplied will be resolvable to the container by other containers on the
		network.
		"""
		is_running = self.is_running()
		if network in self.networks:
			if self.networks[network] == aliases:
				return
			if is_running:
				docker('network', 'disconnect', str(network), self.get_id())
		if is_running:
			docker(
				'network', 'connect',
				*(f'--alias={a}' for a in aliases),
				str(network), self.get_id(),
			)
		self.networks[network] = aliases

	def show_logs(self) -> None:
		"""
		Print the container logs to stdout
		"""
		if self._id:
			docker('logs', self._id)

	def get_exec_args(self, cmd: Arguments, interactive: bool = False) -> MutableArguments:
		"""
		Return a full argument list for running "cmd" inside the container
		"""
		return [DOCKER, "exec", *(("-i",) if interactive else ""), self.get_id(), *coerce_args(cmd)]

	def run(
		self,
		cmd: Arguments,
		*,
		stdin: IO[Any]|int|None = None,
		stdout: IO[Any]|int|None = None,
		stderr: IO[Any]|int|None = None,
		capture_output: bool = False,
		check: bool = False,
		input: bytes|None = None,
		timeout: float|None = None,
	) -> CompletedProcess[bytes]:
		"""
		Run "cmd" to completion inside the container and return the result
		"""
		return run(
			self.get_exec_args(cmd),
			stdin=stdin, stdout=stdout, stderr=stderr,
			capture_output=capture_output,
			check=check, timeout=timeout, input=input,
		)

	def exec(
		self,
		cmd: Arguments,
		*,
		stdin: IO[Any]|int|None = None,
		stdout: IO[Any]|int|None = None,
		stderr: IO[Any]|int|None = None,
	) -> Popen[bytes]:
		"""
		Execute "cmd" inside the container and return a process object once started
		"""
		return Popen(
			self.get_exec_args(cmd),
			stdin=stdin, stdout=stdout, stderr=stderr,
		)


class Network:
	"""
	A Docker network
	"""

	def __init__(self, name: str|None = None) -> None:
		self._name = name or f"br{token_hex(6)}"

	def __str__(self) -> str:
		return self._name

	def __repr__(self) -> str:
		cls = type(self)
		return f"<{cls.__module__}.{cls.__name__} {self._name}>"

	def __eq__(self, other: Any) -> bool:
		if not isinstance(other, Network):
			return self._name == str(other)
		return self._name == other._name

	def __hash__(self) -> int:
		return self._name.__hash__()

	def __enter__(self) -> Network:
		self.create()
		return self

	def __exit__(self, etype: type[BaseException], exc: BaseException, tb: TracebackType) -> None:
		self.destroy()

	@property
	def name(self) -> str:
		return self._name

	def get_id(self) -> str:
		return self._name

	def create(self) -> None:
		"""
		Create the network
		"""
		docker_quiet("network", "create", self._name)

	def destroy(self) -> None:
		"""
		Remove the network
		"""
		docker_quiet("network", "rm", self._name)
