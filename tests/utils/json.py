#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
JSON classes for container types (objects and arrays)
"""

from __future__ import annotations

import json
from typing import Any
from typing import Callable
from typing import TypeVar
from typing import overload

from jsonpath import JSONPath

__all__ = [
	"JSONObject",
	"JSONArray",
]


class JSONPathMixin:

	T = TypeVar('T', bound=object)
	C = TypeVar('C', bound=object)

	@overload
	def path(self, path: str, kind: type[T], convert: None = None) -> T: ...

	@overload
	def path(self, path: str, kind: type[T], convert: Callable[[T], C]) -> C: ...

	def path(self, path: str, kind: type[T], convert: Callable[[T], C]|None = None) -> T|C:
		result = JSONPath(path).parse(self)[0]
		if convert is not None:
			return convert(result)
		elif isinstance(result, kind):
			return result
		raise ValueError(f"{path} is wrong type; expected {kind}; got {type(result)}")


class JSONObject(JSONPathMixin, dict[str, Any]):
	"""
	A dict for JSON objects that implements `.path` for getting child items by a JSON path
	"""

	T = TypeVar("T", bound="JSONObject")

	@classmethod
	def from_string(cls: type[T], string: bytes) -> T:
		return cls(json.loads(string))


class JSONArray(JSONPathMixin, list[Any]):
	"""
	A list for JSON arrays that implements `.path` for getting child items by a JSON path
	"""

	T = TypeVar("T", bound="JSONArray")

	@classmethod
	def from_string(cls: type[T], string: bytes) -> T:
		return cls(json.loads(string))
