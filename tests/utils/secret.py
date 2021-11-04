#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Utility for generating secrets
"""

from __future__ import annotations

import string
from secrets import choice

CHARS = string.ascii_letters + string.digits


def make_secret(size: int) -> str:
	"""
	Generate a string of alphanumeric characters for use as a password
	"""
	return ''.join(choice(CHARS) for _ in range(size))
