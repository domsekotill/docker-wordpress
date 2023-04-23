#  Copyright 2023  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations involving setting configurations in the backend
"""

from __future__ import annotations

from base64 import b32encode as b32
from collections.abc import Iterator
from pathlib import Path
from tempfile import NamedTemporaryFile

from behave import fixture
from behave import given
from behave import then
from behave import use_fixture
from behave import when
from behave.runner import Context
from behave_utils.behave import PatternEnum
from behave_utils.behave import register_pattern
from behave_utils.docker import Cli
from behave_utils.docker import Container
from behave_utils.url import URL
from wp import CURRENT_SITE
from wp import Site
from wp import running_site_fixture
from wp import site_fixture

CONFIG_DIR = Path(__file__).parent.parent / "configs"
DELAYED_SITE = URL("http://delayed.example.com")


register_pattern("\S+", Path)


class Addon(PatternEnum):
	"""
	Addon types for WP; i.e. themes or plugins
	"""

	theme = "theme"
	plugin = "plugin"


class Status(PatternEnum):
	"""
	Status values for `wp {plugin|theme} is-installed` commands

	The values of these enums are the expected return codes from executing one of the above
	commands.
	"""

	active = 0
	inactive = 1


@fixture
def unstarted_site_fixture(context: Context, /, url: URL = CURRENT_SITE) -> Iterator[Site]:
	"""
	Return a wrapper around `wp.site_fixture` that checks the site has not been started
	"""
	site = use_fixture(site_fixture, context, url)
	assert not site.backend.is_running(raise_on_exit=True), \
		'Please run this step after the step "Given the site is not running"'
	yield site


@fixture
def container_file(
	context: Context,
	container: Container,
	path: Path,
	contents: bytes,
) -> Iterator[None]:
	"""
	Create a file in a container as a fixture
	"""
	# For running containers, use commands within the container to make and delete the file
	# This relies on "tee" and "rm" existing in the container image
	if container.is_running():
		run = Cli(container)
		run("tee", path, input=contents)
		yield
		run("rm", path)
		return

	# For unstarted containers, write to a temporary file and add it to the volumes mapping
	with NamedTemporaryFile("wb") as temp:
		temp.write(contents)
		temp.flush()
		container.volumes.append((Path(temp.name), path))
		yield


@given("the site is not running")
def unstarted_site(context: Context) -> None:
	"""
	Mask any current site with a new, unstarted one for the rest of a feature or scenario
	"""
	uid = b32(id(context.feature).to_bytes(10, "big")).decode("ascii")
	use_fixture(site_fixture, context, url=URL(f"http://{uid}.delayed.example.com"))


@given("{fixture:Path} is mounted in {directory:Path}")
@given("{fixture:Path} is mounted in {directory:Path} as {name}")
def mount_volume(
	context: Context,
	fixture: Path,
	directory: Path,
	name: str|None = None,
) -> None:
	"""
	Prepare volume mounts in the backend
	"""
	fixture = CONFIG_DIR / fixture
	if not fixture.exists():
		raise FileNotFoundError(fixture)
	if fixture.is_dir():
		raise IsADirectoryError(fixture)
	if name is None:
		name = fixture.name

	site = use_fixture(unstarted_site_fixture, context, CURRENT_SITE)
	site.backend.volumes.append((fixture.absolute(), directory / name))


@given("{path:Path} exists in the {container_name}")
def create_file(context: Context, path: Path, container_name: str) -> None:
	"""
	Create a file in the named container
	"""
	site = use_fixture(site_fixture, context)
	container = getattr(site, container_name)
	content = context.text.encode("utf-8") if context.text else b"This is a data file!"
	use_fixture(container_file, context, container, path, content)


@given("{path:Path} contains")
def write_file(context: Context, path: Path) -> None:
	"""
	Write the contents of the step's text string to a fixture Path
	"""
	if context.text is None:
		raise ValueError("A text value is needed for this step")
	# If creating a file in /etc/wordpress there is not much point unless the site is
	# unstarted, so use unstarted_site_fixture to ensure it's checked
	site = use_fixture(
		unstarted_site_fixture if Path("/etc/wordpress") in path.parents else site_fixture,
		context,
	)
	content = context.text.encode("utf-8") + b"\n"
	use_fixture(container_file, context, site.backend, path, content)


@given("the environment variable {name} is \"{value}\"")
def set_environment(context: Context, name: str, value: str) -> None:
	"""
	Set the named environment variable in the backend
	"""
	site = use_fixture(unstarted_site_fixture, context, CURRENT_SITE)
	site.backend.env[name] = value


@when("the site is started")
def start_backend(context: Context) -> None:
	"""
	Start the site backend (FPM)
	"""
	use_fixture(running_site_fixture, context, CURRENT_SITE)


@then("the {addon:Addon} {name} is installed")
@then("the {addon:Addon} {name} is {status:Status}")
def is_plugin_installed(
	context: Context,
	addon: Addon,
	name: str,
	status: Status|None = None,
) -> None:
	"""
	Check that the named theme or plugin is installed
	"""
	site = use_fixture(site_fixture, context, CURRENT_SITE)
	assert site.backend.cli(addon.value, "is-installed", name, query=True) == 0, \
		f"{addon.name} {name} is not installed"
	if status is not None:
		assert site.backend.cli(addon.value, "is-active", name, query=True) == status.value


@then("the email address of {user} is \"{value}\"")
@then("the email address of {user} is '{value}'")
def is_user_email(context: Context, user: str, value: str) -> None:
	"""
	Check that the email address of an existing user matches the given value
	"""
	site = use_fixture(site_fixture, context, CURRENT_SITE)
	email = site.backend.cli(
		"user", "get", user, "--field=email",
		deserialiser=lambda mv: str(mv, "utf-8").strip(),
	)
	assert email == value, f"user's email {email} != {value}"


@then("the password of {user} is \"{value}\"")
@then("the password of {user} is '{value}'")
def is_user_password(context: Context, user: str, value: str) -> None:
	"""
	Check that the password of an existing user matches the given value
	"""
	site = use_fixture(site_fixture, context, CURRENT_SITE)
	assert site.backend.cli("user", "check-password", user, value, query=True) == 0, \
		"passwords do not match"


@then("the password of {user} is not \"{value}\"")
@then("the password of {user} is not '{value}'")
def is_not_user_password(context: Context, user: str, value: str) -> None:
	"""
	Check that the password of an existing user does not match the given value
	"""
	site = use_fixture(site_fixture, context, CURRENT_SITE)
	assert site.backend.cli("user", "check-password", user, value, query=True) != 0, \
		"passwords match"
