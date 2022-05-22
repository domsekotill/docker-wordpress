#  Copyright 2021-2022  Dominik Sekotill <dom.sekotill@kodo.org.uk>
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
from os import environ
from typing import TYPE_CHECKING
from typing import Iterator

from behave import fixture
from behave import use_fixture
from behave.model import Feature
from behave.model import Scenario
from behave.runner import Context
from behave_utils import URL
from behave_utils import redirect
from behave_utils.mysql import snapshot_rollback
from requests.sessions import Session
from wp import Site
from wp import test_cluster

if TYPE_CHECKING:
	from behave.runner import FeatureContext
	from behave.runner import ScenarioContext

SITE_URL = URL("http://test.example.com")


def before_all(context: Context) -> None:
	"""
	Setup fixtures for all tests
	"""
	context.site = use_fixture(setup_test_cluster, context, SITE_URL)


def before_feature(context: FeatureContext, feature: Feature) -> None:
	"""
	Setup/revert fixtures before each feature
	"""
	use_fixture(snapshot_rollback, context, context.site.database)


def before_scenario(context: ScenarioContext, scenario: Scenario) -> None:
	"""
	Setup tools for each scenario
	"""
	context.session = use_fixture(requests_session, context)


@fixture
def setup_test_cluster(context: Context, /, site_url: URL) -> Iterator[Site]:
	"""
	Prepare and return the details of a site fixture
	"""
	with test_cluster(site_url) as site:
		yield site


@fixture
def requests_session(context: ScenarioContext, /) -> Iterator[Session]:
	"""
	Create and configure a `requests` session for accessing site fixtures
	"""
	site = context.site
	with Session() as session:
		redirect(session, site.url, site.address)
		yield session


@fixture
def db_snapshot_rollback(context: FeatureContext, /) -> Iterator[None]:
	"""
	Manage the state of a site's database as a revertible fixture
	"""
	db = context.site.database
	snapshot = db.mysqldump("--all-databases", deserialiser=bytes)
	yield
	db.mysql(input=snapshot)


if __name__ == "__main__":
	from subprocess import run

	with test_cluster(SITE_URL) as site:
		run([environ.get("SHELL", "/bin/sh")])

elif not sys.stderr.isatty():
	import logging

	logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
