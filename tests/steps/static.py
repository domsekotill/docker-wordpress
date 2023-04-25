#  Copyright 2022-2023  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations involving creating files in containers
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator

from behave import fixture
from behave import given
from behave import use_fixture
from behave.runner import Context
from behave_utils.docker import Cli
from behave_utils.docker import Container
from wp import running_site_fixture


@given("{path:Path} exists in the {container_name}")
def step_impl(context: Context, path: Path, container_name: str) -> None:
	"""
	Create a file in the named container
	"""
	site = use_fixture(running_site_fixture, context)
	container = getattr(site, container_name)
	use_fixture(container_file, context, path, container)


@fixture
def container_file(context: Context, path: Path, container: Container) -> Iterator[None]:
	"""
	Create a file in a container as a fixture
	"""
	text = context.text.encode("utf-8") if context.text else b"This is a data file!"

	# For running containers, use commands within the container to make and delete the file
	# This relies on "tee" and "rm" existing in the container image
	if container.is_running():
		run = Cli(container)
		run("tee", path, input=text)
		yield
		run("rm", path)
		return

	# For unstarted containers, write to a temporary file and add it to the volumes mapping
	with NamedTemporaryFile("wb") as temp:
		temp.write(text)
		temp.close()
		container.volumes.append((path, Path(temp.name)))
		yield
