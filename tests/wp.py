#  Copyright 2021-2022  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Management and control for WordPress fixtures
"""

from __future__ import annotations

from contextlib import contextmanager
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Iterator
from typing import TypeVar

from behave import fixture
from behave import use_fixture
from behave.runner import Context
from behave_utils import URL
from behave_utils import wait
from behave_utils.docker import Cli
from behave_utils.docker import Container as Container
from behave_utils.docker import Image
from behave_utils.docker import IPv4Address
from behave_utils.docker import Network
from behave_utils.mysql import Mysql

BUILD_CONTEXT = Path(__file__).parent.parent
DEFAULT_URL = URL("http://test.example.com")


class Wordpress(Container):
	"""
	Container subclass for a WordPress PHP-FPM container
	"""

	DEFAULT_ALIASES = ("upstream",)

	if TYPE_CHECKING:
		T = TypeVar("T", bound="Wordpress")

	def __init__(self, site_url: URL, database: Mysql, network: Network|None = None):
		Container.__init__(
			self,
			Image.build(
				BUILD_CONTEXT,
				php_version=environ.get("PHP_VERSION"),
				wp_version=environ.get("WP_VERSION"),
			),
			volumes=[
				("static", Path("/app/static")),
				("media", Path("/app/media")),
			],
			env=dict(
				SITE_URL=site_url,
				SITE_ADMIN_EMAIL="test@kodo.org.uk",
				DB_NAME=database.name,
				DB_USER=database.user,
				DB_PASS=database.password,
				DB_HOST=database.get_location(),
			),
			network=network,
		)

	@property
	def cli(self) -> Cli:
		"""
		Run WP-CLI commands
		"""
		return Cli(self, "wp")

	@contextmanager
	def started(self: T) -> Iterator[T]:
		with self:
			self.start()
			cmd = ["bash", "-c", "[[ /proc/1/exe -ef `which php-fpm` ]]"]
			wait(lambda: self.is_running() and self.run(cmd).returncode == 0, timeout=600)
			yield self


class Nginx(Container):
	"""
	Container subclass for an Nginx frontend
	"""

	def __init__(self, backend: Wordpress, network: Network|None = None):
		Container.__init__(
			self,
			Image.build(
				BUILD_CONTEXT,
				target='nginx',
				nginx_version=environ.get("NGINX_VERSION"),
			),
			network=network,
			volumes=backend.volumes,
		)


class Site:
	"""
	Manage all the containers of a site fixture
	"""

	if TYPE_CHECKING:
		T = TypeVar("T", bound="Site")

	def __init__(
		self,
		url: URL,
		network: Network,
		frontend: Nginx,
		backend: Wordpress,
		database: Mysql,
	):
		self.url = url
		self.network = network
		self.frontend = frontend
		self.backend = backend
		self.database = database
		self._address: IPv4Address|None = None

	@classmethod
	@contextmanager
	def build(cls: type[T], site_url: URL) -> Iterator[T]:
		test_dir = Path(__file__).parent
		db_init = test_dir / "mysql-init.sql"

		with Network() as network, Mysql(network=network, init_files=[db_init]) as database:
			database.start()  # Get a head start on initialising the database
			with \
				Wordpress(site_url, database, network=network) as backend, \
				Nginx(backend, network=network) as frontend:
					yield cls(site_url, network, frontend, backend, database)

	@contextmanager
	def running(self: T) -> Iterator[T]:
		"""
		Start all the services and configure the network
		"""
		with self.database.started(), self.backend.started(), self.frontend.started():
			try:
				yield self
			finally:
				self._address = None

	@property
	def address(self) -> IPv4Address:
		if self._address is None:
			if not self.frontend.is_running():
				raise RuntimeError(
					"Site.address may only be accessed inside a Site.running() context",
				)
			self._address = self.frontend.inspect().path(
				f"$.NetworkSettings.Networks.{self.network}.IPAddress",
				str, IPv4Address,
			)
		return self._address


@fixture
def site_fixture(context: Context, /, site_url: URL|None = None) -> Iterator[Site]:
	"""
	Return a currently in-scope Site instance when used with `use_fixture`

	If "site_url" is provided and it doesn't match a current Site instance, a new instance
	will be created in the current context.

	>>> use_fixture(site_fixture, context)
	<<< <wp.Site at [...]>
	"""
	if hasattr(context, "site"):
		assert isinstance(context.site, Site)
		if site_url is None or context.site.url == site_url:
			yield context.site
			return
	with Site.build(site_url or DEFAULT_URL) as context.site:
		yield context.site


@fixture
def running_site_fixture(context: Context, /, site_url: URL|None = None) -> Iterator[Site]:
	"""
	Return a currently in-scope Site instance that is running when used with `use_fixture`

	Like `site_fixture` but additionally entered into the `Site.running` context manager.
	"""
	with use_fixture(site_fixture, context, site_url=site_url).running() as site:
		yield site
