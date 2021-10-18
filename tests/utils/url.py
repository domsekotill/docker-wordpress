#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
URL types and pattern matcher
"""

from __future__ import annotations

from urllib.parse import urljoin

from .behave import register_pattern


@register_pattern(r"(?:https?://\S+|/\S*)")
class URL(str):
	"""
	A subclass for URL strings which also acts as a pattern match type
	"""

	def __truediv__(self, other: str) -> URL:
		return URL(urljoin(self, other))

	def __add__(self, other: str) -> URL:
		return URL(str(self) + other)
