#  Copyright 2021-2023  Dominik Sekotill <dom.sekotill@kodo.org.uk>
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
from typing import Iterator

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
from behave_utils.docker import inspect
from behave_utils.mysql import Mysql
from typing_extensions import Self

BUILD_CONTEXT = Path(__file__).parent.parent
DEFAULT_URL = URL("http://test.example.com")
CURRENT_SITE = URL("current://")


class Wordpress(Container):
	"""
	Container subclass for a WordPress PHP-FPM container
	"""

	DEFAULT_ALIASES = ("upstream",)

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
	def started(self) -> Iterator[Self]:
		"""
		Return a context in which the container is guaranteed to be started and running
		"""
		with self:
			self.start()
			cmd = ["bash", "-c", "[[ /proc/1/exe -ef `which php-fpm` ]]"]
			wait(lambda: self.run(cmd).returncode == 0, timeout=600)
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
		self._running = False

	@classmethod
	@contextmanager
	def build(cls, site_url: URL) -> Iterator[Self]:
		"""
		Return a context that constructs a ready-to-go instance on entry
		"""
		with (
			Network() as network,
			Mysql(network=network) as database,
			Wordpress(site_url, database, network=network) as backend,
			Nginx(backend, network=network) as frontend,
		):
			yield cls(site_url, network, frontend, backend, database)

	@contextmanager
	def running(self) -> Iterator[Self]:
		"""
		Return a context in which all containers are guaranteed to be started and running
		"""
		if self._running:
			yield self
			return
		self._running = True
		with self.backend.started(), self.frontend.started():
			try:
				yield self
			finally:
				self._running = False
				self._address = None

	@property
	def address(self) -> IPv4Address:
		"""
		Return an IPv4 address through which test code can access the site
		"""
		if self._address is None:
			if not self.frontend.is_running():
				raise RuntimeError(
					"Site.address may only be accessed inside a Site.running() context",
				)
			self._address = inspect(self.frontend).path(
				f"$.NetworkSettings.Networks.{self.network}.IPAddress",
				str, IPv4Address,
			)
		return self._address


@fixture
def site_fixture(context: Context, /, url: URL = CURRENT_SITE) -> Iterator[Site]:
	"""
	Return a currently in-scope Site instance when used with `use_fixture`

	If "url" is provided and it doesn't match a current Site instance, a new instance
	will be created in the current context.

	>>> use_fixture(site_fixture, context)
	<<< <wp.Site at [...]>
	"""
	if not hasattr(context, "sites"):
		context.sites = dict[URL, Site]()
	assert len(context.sites) == 0 or \
		len(context.sites) >= 2 and CURRENT_SITE in context.sites, \
		f'Both ["url" or DEFAULT_URL] and [CURRENT_SITE] must be added to sites: ' \
		f'{context.sites!r}'
	if url in context.sites:
		yield context.sites[url]
		return
	url = DEFAULT_URL if url == CURRENT_SITE else url
	prev = context.sites.get(CURRENT_SITE)
	with Site.build(url) as context.sites[url]:
		context.sites[CURRENT_SITE] = context.sites[url]
		yield context.sites[url]
	del context.sites[url]
	del context.sites[CURRENT_SITE]
	if prev:
		context.sites[CURRENT_SITE] = prev


@fixture
def running_site_fixture(context: Context, /, url: URL = CURRENT_SITE) -> Iterator[Site]:
	"""
	Return a currently in-scope Site instance that is running when used with `use_fixture`

	Like `site_fixture` but additionally entered into the `Site.running` context manager.
	"""
	with use_fixture(site_fixture, context, url=url).running() as site:
		yield site
