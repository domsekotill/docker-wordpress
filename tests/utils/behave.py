#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Utilities for "behave" interactions
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import TypeVar
from typing import overload

import behave
import parse

T = TypeVar("T")

__all__ = [
	"PatternEnum",
	"register_pattern",
]


class PatternConverter(Protocol):

	__name__: str

	def __call__(self, match: str) -> Any: ...


class Decorator(Protocol[T]):

	def __call__(self, converter: T) -> T: ...


@overload
def register_pattern(pattern: str) -> Decorator[PatternConverter]: ...


@overload
def register_pattern(pattern: str, converter: PatternConverter) -> PatternConverter: ...


def register_pattern(pattern: str, converter: PatternConverter|None = None) -> PatternConverter|Decorator[PatternConverter]:
	"""
	Register a pattern and converter for a step parser type

	The type is named after the converter.
	"""
	pattern_decorator = parse.with_pattern(pattern)

	def decorator(converter: PatternConverter) -> PatternConverter:
		behave.register_type(**{converter.__name__: pattern_decorator(converter)})
		return converter

	if converter:
		return decorator(converter)
	return decorator


class EnumMeta(enum.EnumMeta):

	MEMBERS = 'members'

	T = TypeVar("T", bound="EnumMeta")

	def __new__(mtc: type[T], name: str, bases: tuple[type, ...], attr: dict[str, Any], **kwds: Any) -> T:
		member_names: list[str] = attr._member_names  # type: ignore
		if mtc.MEMBERS in member_names:
			members = attr.pop(mtc.MEMBERS)
			member_names.remove(mtc.MEMBERS)
			member_names.extend(members)
			attr.update(members)
		cls = enum.EnumMeta.__new__(mtc, name, bases, attr, **kwds)
		decorator = parse.with_pattern('|'.join(member for member in cls.__members__))
		behave.register_type(**{name: decorator(cls)})
		return cls


class PatternEnum(enum.Enum, metaclass=EnumMeta):
	"""
	An enum class that self registers as a pattern type for step implementations

	Enum names are used to match values in step texts, so a value can be aliased multiple
	times to provide alternates for matching, including alternative languages.
	To supply names that are not valid identifiers the functional Enum API must be used,
	supplying mapped values:
	https://docs.python.org/3/library/enum.html#functional-api

	Enum values may be anything meaningful; for instance a command keyword that identifies a
	type.
	"""

	if TYPE_CHECKING:
		C = TypeVar("C", bound="PatternEnum")

	@classmethod
	def _missing_(cls: type[C], key: Any) -> C:
		return cls[key]
