#  Copyright 2022-2023  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations involving creating files in containers
"""

from __future__ import annotations

from typing import Iterator

from behave import fixture
from behave import given
from behave import use_fixture
from behave.runner import Context
from behave_utils.docker import Cli
from wp import running_site_fixture


@given("{path} exists in the {container}")
def step_impl(context: Context, path: str, container: str) -> None:
	"""
	Create a file in the named container
	"""
	use_fixture(container_file, context, path, container)


@fixture
def container_file(context: Context, path: str, container_name: str) -> Iterator[None]:
	"""
	Create a file in a named container as a fixture
	"""
	site = use_fixture(running_site_fixture, context)
	container = getattr(site, container_name)
	run = Cli(container)
	run("tee", path, input=(context.text or "This is a data file!"))
	yield
	run("rm", path)
