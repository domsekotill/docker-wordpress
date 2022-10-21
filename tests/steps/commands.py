#  Copyright 2021-2022  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations involving running commands in fixture containers
"""

from __future__ import annotations

import json
import shlex
from typing import TYPE_CHECKING

from behave import then
from behave import when
from behave_utils.behave import PatternEnum
from behave_utils.behave import register_pattern
from wp import Container

if TYPE_CHECKING:
	from behave.runner import Context


@register_pattern(r".+")
class Arguments(list[str]):
	"""
	Step pattern for command lines
	"""

	def __init__(self, cmdline: str):
		self.extend(shlex.split(cmdline))


class Stream(PatternEnum):
	"""
	Pattern matching enum for stdio stream names
	"""

	STDOUT = "stdout"
	STDERR = "stderr"

	stdout = STDOUT
	stderr = STDERR


@when(""""{args:Arguments}" is run""")
@when("""'{args:Arguments}' is run""")
def run_command(context: Context, args: Arguments) -> None:
	"""
	Run a command in the appropriate site container
	"""
	if len(args) == 0:
		raise ValueError("No arguments in argument list")
	if args[0] in ('wp', 'php'):
		container: Container = context.site.backend
	else:
		raise ValueError(f"Unknown command: {args[0]}")
	context.process = container.run(args, capture_output=True)


@then("nothing is seen from {stream:Stream}")
def check_empty_stream(context: Context, stream: Stream) -> None:
	"""
	Check there is no output on the given stream of a previous command
	"""
	output = getattr(context.process, stream.value)
	assert not output, f"Unexpected output seen from {stream.name}: {output}"


@then("JSON is seen from {stream:Stream}")
def check_json_stream(context: Context, stream: Stream) -> None:
	"""
	Check there is no output on the given stream of a previous command
	"""
	output = getattr(context.process, stream.value)
	try:
		json.loads(output)
	except json.JSONDecodeError:
		raise AssertionError(f"Expecting JSON from {stream.name}; got {output}")


@then('"{response}" is seen from {stream:Stream}')
def check_stream(context: Context, response: str, stream: Stream) -> None:
	"""
	Check the output streams of a previous command for the given response
	"""
	output = getattr(context.process, stream.value)
	assert output.strip() == response.encode(), \
		f"Expected output from {stream.name}: {response.encode()!r}\ngot: {output!r}"
