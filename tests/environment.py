#  Copyright 2021-2023  Dominik Sekotill <dom.sekotill@kodo.org.uk>
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
from typing import TYPE_CHECKING

from behave import use_fixture
from behave.model import Feature
from behave.model import Scenario
from behave.runner import Context
from behave_utils import URL
from behave_utils.mysql import snapshot_rollback
from wp import running_site_fixture

if TYPE_CHECKING:
	from behave.runner import FeatureContext
	from behave.runner import ScenarioContext

SITE_URL = URL("http://test.example.com")


def before_all(context: Context) -> None:
	"""
	Setup fixtures for all tests
	"""
	use_fixture(running_site_fixture, context, site_url=SITE_URL)


def before_feature(context: FeatureContext, feature: Feature) -> None:
	"""
	Setup/revert fixtures before each feature
	"""
	use_fixture(snapshot_rollback, context, context.site.database)


def before_scenario(context: ScenarioContext, scenario: Scenario) -> None:
	"""
	Setup tools for each scenario
	"""


if not sys.stderr.isatty():
	import logging

	logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
