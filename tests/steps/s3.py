#  Copyright 2024  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations involving S3 integrations with a site
"""

from __future__ import annotations

import enum
from pathlib import Path

from behave import given
from behave import then
from behave import use_fixture
from behave.runner import Context
from behave_utils.behave import PatternEnum
from minio import bucket_fixture
from minio import current_bucket_fixture
from wp import site_fixture


class BucketStyle(PatternEnum):
	"""
	An enum of the two types of S3 bucket: subdomain or path-based
	"""

	path = enum.auto()
	subdomain = enum.auto()


@given("the site is configured to use S3")
@given("the site is configured to use S3 with {style:BucketStyle} buckets")
def configure_site(context: Context, style: BucketStyle = BucketStyle.path) -> None:
	"""
	Create a Minio fixture and configure the current (unstarted) site to use it
	"""
	site = use_fixture(site_fixture, context)
	bucket = use_fixture(bucket_fixture, context, site, style is BucketStyle.subdomain)
	site.backend.env.update(
		S3_MEDIA_ENDPOINT=bucket.url,
		S3_MEDIA_KEY=bucket.key,
		S3_MEDIA_SECRET=bucket.secret,
	)


@then("the S3 bucket has {path:Path}")
def bucket_has(context: Context, path: Path) -> None:
	"""
	Check to see that a configured Minio bucket has the given path in it
	"""
	bucket = use_fixture(current_bucket_fixture, context)
	assert bucket.has_path(path)
