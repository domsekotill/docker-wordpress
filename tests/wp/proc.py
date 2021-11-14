#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Manage processes asynchronously
"""

from __future__ import annotations

import io
import logging
import os
import sys
from subprocess import DEVNULL
from subprocess import PIPE
from typing import IO
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Mapping
from typing import MutableSequence
from typing import Sequence
from typing import TypeVar
from typing import Union
from typing import overload

import trio.abc

T = TypeVar('T')
Deserialiser = Callable[[bytes], T]

PathLike = os.PathLike[str]
PathArg = Union[PathLike, str]
Arguments = Sequence[PathArg]
MutableArguments = MutableSequence[PathArg]
Environ = Mapping[str, str]

_logger = logging.getLogger(__name__)


def coerce_args(args: Arguments) -> Iterator[str]:
	"""
	Ensure path-like arguments are converted to strings
	"""
	return (os.fspath(a) for a in args)


@overload
def exec_io(
	cmd: Arguments,
	data: bytes = b'',
	deserialiser: Deserialiser[T] = ...,
	**kwargs: Any,
) -> T: ...


@overload
def exec_io(
	cmd: Arguments,
	data: bytes = b'',
	deserialiser: None = None,
	**kwargs: Any,
) -> int: ...


def exec_io(
	cmd: Arguments,
	data: bytes = b'',
	deserialiser: Deserialiser[Any]|None = None,
	**kwargs: Any,
) -> Any:
	"""
	Execute a command, handling output asynchronously

	If data is provided it will be fed to the process' stdin.
	If a deserialiser is provided it will be used to parse stdout data from the process.

	Stderr and stdout (if no deserialiser is provided) will be written to `sys.stderr` and
	`sys.stdout` respectively.

	Note that the data is written, not redirected.  If either `sys.stdout` or `sys.stderr`
	is changed to an IO-like object with no file descriptor, this will still work.
	"""
	if deserialiser and 'stdout' in kwargs:
		raise TypeError("Cannot provide 'deserialiser' with 'stdout' argument")
	if data and 'stdin' in kwargs:
		raise TypeError("Cannot provide 'data' with 'stdin' argument")
	stdout: IO[str]|IO[bytes]|int = io.BytesIO() if deserialiser else kwargs.pop('stdout', sys.stdout)
	stderr: IO[str]|IO[bytes]|int = kwargs.pop('stderr', sys.stderr)
	_logger.debug("executing: %s", cmd)
	proc = trio.run(_exec_io, cmd, data, stdout, stderr, kwargs)
	if deserialiser:
		assert isinstance(stdout, io.BytesIO)
		return deserialiser(stdout.getvalue())
	return proc.returncode


async def _exec_io(
	cmd: Arguments,
	data: bytes,
	stdout: IO[str]|IO[bytes]|int,
	stderr: IO[str]|IO[bytes]|int,
	kwargs: dict[str, Any],
) -> trio.Process:
	proc = await trio.open_process(
		[*coerce_args(cmd)],
		stdin=PIPE if data else DEVNULL,
		stdout=PIPE,
		stderr=PIPE,
		**kwargs,
	)
	async with proc, trio.open_nursery() as nursery:
		assert proc.stdout is not None and proc.stderr is not None
		nursery.start_soon(_passthru, proc.stderr, stderr)
		nursery.start_soon(_passthru, proc.stdout, stdout)
		if data:
			assert proc.stdin is not None
			async with proc.stdin as stdin:
				await stdin.send_all(data)
	return proc


async def _passthru(in_stream: trio.abc.ReceiveStream, out_stream: IO[str]|IO[bytes]|int) -> None:
	try:
		if not isinstance(out_stream, int):
			out_stream = out_stream.fileno()
	except (OSError, AttributeError):
		# cannot get file descriptor, probably a memory buffer
		if isinstance(out_stream, io.BytesIO):
			async def write(data: bytes) -> None:
				assert isinstance(out_stream, io.BytesIO)
				out_stream.write(data)
		elif isinstance(out_stream, io.StringIO):
			async def write(data: bytes) -> None:
				assert isinstance(out_stream, io.StringIO)
				out_stream.write(data.decode())
		else:
			raise TypeError(f"Unknown IO type: {type(out_stream)}")
	else:
		# is/has a file descriptor, out_stream is now that file descriptor
		async def write(data: bytes) -> None:
			assert isinstance(out_stream, int)
			data = memoryview(data)
			remaining = len(data)
			while remaining:
				await trio.lowlevel.wait_writable(out_stream)
				written = os.write(out_stream, data)
				data = data[written:]
				remaining -= written

	while True:
		data = await in_stream.receive_some()
		if not data:
			return
		await write(data)
