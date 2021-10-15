#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations dealing with HTTP requests
"""

from __future__ import annotations

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
	not_found = 404

	members = {
		"200": 200, "OK": 200,
		"404": 404, "Not Found": 404,
	}


@when("{url:URL} is requested")
def get_request(context: Context, url: URL) -> None:
	"""
	Assign the response from making a GET request to "url" to the context
	"""
	context.response = context.session.get(context.site.url / url)


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
	assert context.response.status_code == response
