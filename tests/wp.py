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

from behave_utils import URL
from behave_utils import wait
from behave_utils.docker import Cli
from behave_utils.docker import Container as Container
from behave_utils.docker import Image
from behave_utils.docker import IPv4Address
from behave_utils.docker import Network
from behave_utils.mysql import Mysql

BUILD_CONTEXT = Path(__file__).parent.parent


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

		with Network() as network:
			database = Mysql(network=network, init_files=[db_init])
			database.start()  # Get a head start on initialising the database
			backend = Wordpress(site_url, database, network=network)
			frontend = Nginx(backend, network=network)
			yield cls(site_url, network, frontend, backend, database)

	@contextmanager
	def running(self) -> Iterator[None]:
		"""
		Start all the services and configure the network
		"""
		with self.database.started(), self.backend.started(), self.frontend.started():
			try:
				yield
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


@contextmanager
def test_cluster(site_url: URL) -> Iterator[Site]:
	"""
	Configure and start all the necessary containers for use as test fixtures

	Deprecated: this is now a wrapper around Site.build() and Site.running()
	"""
	with Site.build(site_url) as site, site.running():
		yield site
