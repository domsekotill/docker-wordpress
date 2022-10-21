#  Copyright 2021-2022  Dominik Sekotill <dom.sekotill@kodo.org.uk>
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
from behave_utils import URL
from behave_utils import PatternEnum

SAMPLE_SITE_NAME = "http://test.example.com"


class Method(PatternEnum):
	"""
	HTTP methods
	"""

	GET = "GET"
	POST = "POST"
	PUT = "PUT"
	# add more methods as needed…


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
	method_not_allowed = 405

	# Aliases for the above codes, for mapping natural language in feature files to enums
	ALIASES = {
		"OK": 200,
		"Not Found": 404,
		"Method Not Allowed": 405,
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


@when("data is sent with {method:Method} to {url:URL}")
def post_request(context: Context, method: Method, url: URL) -> None:
	"""
	Send context text to a URL endpoint and assign the response to the context
	"""
	if context.text is None:
		raise ValueError("Missing data, please add as text to step definition")
	context.response = context.session.request(
		method.value,
		context.site.url / url,
		data=context.text.strip().format(context=context).encode("utf-8"),
		allow_redirects=False,
	)


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


@then('''the "{header_name}" header's value is "{header_value}"''')
def assert_header(context: Context, header_name: str, header_value: str) -> None:
	"""
	Assert that an expected header was received during a previous step
	"""
	if SAMPLE_SITE_NAME in header_value:
		header_value = header_value.replace(SAMPLE_SITE_NAME, context.site.url)
	headers = context.response.headers
	assert header_name in headers, \
		f"Expected header not found in response: {header_name!r}"
	assert headers[header_name] == header_value, \
		f"Expected header value not found: got {headers[header_name]!r}"


@then("the response body is JSON")
def assert_is_json(context: Context) -> None:
	"""
	Assert the response body of a previous step contains a JSON document
	"""
	try:
		context.response.json()
	except json.JSONDecodeError:
		raise AssertionError("Response is not a JSON document")
