#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Step implementations involving creating and requesting WP posts (and pages)
"""

from __future__ import annotations

from codecs import decode as utf8_decode
from typing import Any
from typing import Iterator

from behave import fixture
from behave import given
from behave import then
from behave import use_fixture
from behave import when
from behave.runner import Context
from request_steps import get_request
from utils import URL
from utils import JSONArray
from utils import JSONObject
from utils import PatternEnum

DEFAULT_CONTENT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""


class PostType(PatternEnum):
	"""
	Enumeration for matching WP post types in step texts
	"""

	post = "post"
	page = "page"


@given("{path} does not exist")
def assert_not_exist(context: Context, path: str) -> None:
	"""
	Assert that the path does not route to any resource
	"""
	cmd = [
		"post", "list", "--field=url", "--format=json",
		"--post_type=post,page", "--post_status=publish",
	]
	urls = {*context.site.backend.cli(*cmd, deserialiser=JSONArray.from_string)}
	assert context.site.url / path not in urls


@given("a {post_type:PostType} exists containing")
def create_post(context: Context, post_type: PostType, text: str|None = None) -> None:
	"""
	Create a WP post of the given type and store it in the context with the type as the name
	"""
	post = use_fixture(wp_post, context, post_type, text or context.text)
	setattr(context, post_type.value, post)


@given("the page is configured as the homepage")
def set_homepage(context: Context) -> None:
	"""
	Set the WP page from the context as the configured front page
	"""
	wp = context.site.backend
	pageid = context.page.path("$.ID", int)
	wp.cli("option", "update", "page_on_front", str(pageid))
	wp.cli("option", "update", "show_on_front", "page")

	page = use_fixture(wp_post, context, PostType.page)
	wp.cli("option", "update", "page_for_posts", page.path("$.ID", int, str))


@given("the homepage is the default")
def reset_homepage(context: Context) -> None:
	"""
	Ensure the front page is reverted to it's default
	"""
	context.site.backend.cli("option", "update", "show_on_front", "post")


@when("the {post_type:PostType} is requested")
def request_page(context: Context, post_type: PostType) -> None:
	"""
	Request the specified WP post of the given type in the context
	"""
	post = getattr(context, post_type.value)
	get_request(context, post.path("$.url", URL))


@when("the {post_type:PostType} suffixed with {suffix} is requested")
def request_page_with_suffix(context: Context, post_type: PostType, suffix: str) -> None:
	"""
	Like `request_page`, with additional URL components appended to the post's URL
	"""
	post = getattr(context, post_type.value)
	get_request(context, post.path("$.url", URL) + suffix)


@then("we will see the {post_type:PostType} text")
def assert_contains(
	context: Context,
	post_type: PostType = PostType.post,
	text: str|None = None,
) -> None:
	"""
	Assert that the text is in the response from a previous step

	The text can be supplied directly or taken from a WP post of the type specified, taken
	from the context.
	"""
	if not text:
		post = getattr(context, post_type.value)
		text = post.path("$.post_content", str)
	assert text in context.response.text


@fixture
def wp_post(
	context: Context, /,
	post_type: PostType|None = None,
	content: str = DEFAULT_CONTENT,
	*a: Any,
	**k: Any,
) -> Iterator[JSONObject]:
	"""
	Create a WP post fixture of the given type with the given content
	"""
	assert post_type is not None, \
		"post_type MUST be supplied to use_fixture when calling with wp_post"

	wp = context.site.backend
	postid = wp.cli(
		"post", "create",
		f"--post_type={post_type.value}", "--post_status=publish",
		f"--post_name=test-{post_type.value}",
		f"--post_title=Test {post_type.name.capitalize()}",
		"-", "--porcelain",
		input=content, deserialiser=utf8_decode,
	).strip()
	post = wp.cli("post", "get", postid, "--format=json", deserialiser=JSONObject.from_string)
	post.update(
		url=URL(
			wp.cli(
				"post", "list", "--field=url",
				f"--post__in={postid}", f"--post_type={post_type.value}",
				deserialiser=utf8_decode,
			).strip(),
		),
	)
	yield post
	wp.cli("post", "delete", postid)
