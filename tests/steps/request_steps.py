#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations dealing with HTTP requests
"""

from __future__ import annotations

import json
from typing import Any

from behave import then
from behave import when
from behave.runner import Context
from utils import URL
from utils import PatternEnum


class ResponseCode(int, PatternEnum):
	"""
	HTTP response codes
	"""

	ok = 200
	moved_permanently = 301
	found = 302
	not_modified = 304
	temporary_redirect = 307
	permanent_redirect = 308
	not_found = 404

	# Aliases for the above codes, for mapping natural language in feature files to enums
	ALIASES = {
		"OK": 200,
		"Not Found": 404,
	}

	@staticmethod
	def member_filter(attr: dict[str, Any], member_names: list[str]) -> None:
		"""
		Add natural language aliases and stringified code values to members

		Most will be accessible only though a class call, which is acceptable as that is how
		step implementations look up the values.
		"""
		additional = {
			str(value): value
			for name in member_names
			for value in [attr[name]]
			if isinstance(value, int)
		}
		additional.update(attr["ALIASES"])
		member_names.remove("ALIASES")
		member_names.extend(additional)
		attr.update(additional)


@when("{url:URL} is requested")
def get_request(context: Context, url: URL) -> None:
	"""
	Assign the response from making a GET request to "url" to the context
	"""
	context.response = context.session.get(context.site.url / url, allow_redirects=False)


@when("the homepage is requested")
def get_homepage(context: Context) -> None:
	"""
	Assign the response from making a GET request to the base URL to the context
	"""
	get_request(context, '/')


@then('"{response:ResponseCode}" is returned')
@then('{response:ResponseCode} is returned')
def assert_response(context: Context, response: ResponseCode) -> None:
	"""
	Assert that the expected response was received during a previous step

	"response" can be a numeric or phrasal response in ResponseCode
	"""
	assert context.response.status_code == response, \
		f"Expected response {response}: got {context.response.status_code}"


@then("the response body is JSON")
def assert_is_json(context: Context) -> None:
	"""
	Assert the response body of a previous step contains a JSON document
	"""
	try:
		context.response.json()
	except json.JSONDecodeError:
		raise AssertionError("Response is not a JSON document")
