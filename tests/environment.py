#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Setup module for Behave tests

This module prepares test fixtures and global context items.

https://behave.readthedocs.io/en/stable/tutorial.html#environmental-controls
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import NamedTuple

from behave import fixture
from behave import use_fixture
from behave.model import Feature
from behave.model import Scenario
from behave.runner import Context
from requests.sessions import Session
from utils import URL
from utils import make_secret
from utils import redirect
from wp import Mysql
from wp import Wordpress
from wp.docker import Container
from wp.docker import Image
from wp.docker import IPv4Address
from wp.docker import Network

if TYPE_CHECKING:
	from behave.runner import FeatureContext
	from behave.runner import ScenarioContext

SITE_URL = URL("http://test.example.com")
BUILD_CONTEXT = Path(__file__).parent.parent


def before_all(context: Context) -> None:
	"""
	Setup fixtures for all tests
	"""
	context.site = use_fixture(setup_test_cluster, context, SITE_URL)


def before_feature(context: FeatureContext, feature: Feature) -> None:
	"""
	Setup/revert fixtures before each feature
	"""
	use_fixture(db_snapshot_rollback, context)


def before_scenario(context: ScenarioContext, scenario: Scenario) -> None:
	"""
	Setup tools for each scenario
	"""
	context.session = use_fixture(requests_session, context)


class Site(NamedTuple):
	"""
	A named-tuple of information about the containers for a site fixture
	"""

	url: str
	address: IPv4Address
	frontend: Container
	backend: Wordpress
	database: Mysql


# Todo(dom.sekotill): When PEP-612 is properly implemented in mypy the [*a, **k] and default
# values nonsense can be removed from fixtures

@fixture
def setup_test_cluster(context: Context, /, site_url: str|None = None, *a: Any, **k: Any) -> Iterator[Site]:
	"""
	Prepare and return the details of a site fixture
	"""
	assert site_url is not None, \
		"site_url is required, but default supplied until PEP-612 supported"
	with test_cluster(site_url) as site:
		yield site


@fixture
def requests_session(context: ScenarioContext, /, *a: Any, **k: Any) -> Iterator[Session]:
	"""
	Create and configure a `requests` session for accessing site fixtures
	"""
	site = context.site
	with Session() as session:
		redirect(session, site.url, site.address)
		yield session


@fixture
def db_snapshot_rollback(context: FeatureContext, /, *a: Any, **k: Any) -> Iterator[None]:
	"""
	Manage the state of a site's database as a revertible fixture
	"""
	db = context.site.database
	snapshot = db.mysqldump("--all-databases", deserialiser=bytes)
	yield
	db.mysql(input=snapshot)


@contextmanager
def test_cluster(site_url: str) -> Iterator[Site]:
	"""
	Configure and start all the necessary containers for use as test fixtures
	"""
	test_dir = Path(__file__).parent

	db_secret = make_secret(20)
	db_init = test_dir / "mysql-init.sql"

	with Network() as network:
		database = Mysql(
			Image.pull("mysql/mysql-server"),
			network=network,
			volumes={
				Path("/var/lib/mysql"),
				(db_init, Path("/docker-entrypoint-initdb.d") / db_init.name),
			},
			env=dict(
				MYSQL_DATABASE="test-db",
				MYSQL_USER="test-db-user",
				MYSQL_PASSWORD=db_secret,
			),
		)
		frontend = Container(
			Image.build(BUILD_CONTEXT, target='nginx'),
			network=network,
			volumes=[
				("static", Path("/app/static")),
				("media", Path("/app/media")),
			],
		)
		backend = Wordpress(
			Image.build(BUILD_CONTEXT),
			network=network,
			volumes=frontend.volumes,
			env=dict(
				SITE_URL=site_url,
				SITE_ADMIN_EMAIL="test@kodo.org.uk",
				DB_NAME="test-db",
				DB_USER="test-db-user",
				DB_PASS=db_secret,
				DB_HOST="database:3306",
			),
		)

		backend.connect(network, "upstream")
		database.connect(network, "database")

		with database.started(), backend.started(), frontend.started():
			addr = frontend.inspect(
				f"$.NetworkSettings.Networks.{network}.IPAddress",
				str, IPv4Address,
			)
			yield Site(site_url, addr, frontend, backend, database)


if __name__ == "__main__":
	from os import environ
	from subprocess import run

	with test_cluster(SITE_URL) as site:
		run([environ.get("SHELL", "/bin/sh")])

elif not sys.stderr.isatty():
	import logging

	logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
