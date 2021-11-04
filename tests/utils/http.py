#  Copyright 2021  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Extensions for "requests"
"""

from __future__ import annotations

import ipaddress
from typing import Any
from typing import Mapping
from urllib.parse import urlparse

import requests.adapters
from requests.packages.urllib3 import connection
from requests.packages.urllib3 import connectionpool


def redirect(session: requests.Session, prefix: str, address: ipaddress.IPv4Address) -> None:
	"""
	Redirect all requests for "prefix" to a given address

	This function allows a user to completely override DNS and local name lookups, allowing
	fixtures to be contacted via any configured URL without having to mess with the system's
	name resolution services.

	"prefix" is formated as either "{hostname}[:{port}]" or "{schema}://{hostname}[:{port}]"
	where "schema" defaults to (and currently only supports) "http".
	"""
	if prefix.startswith("https://"):
		raise ValueError("https:// prefixes not currently supported")
	if not prefix.startswith("http://"):
		prefix = f"http://{prefix}"
	session.mount(prefix, LocalHTTPAdapter(address))


class LocalHTTPAdapter(requests.adapters.HTTPAdapter):
	"""
	An alternative HTTP adapter that directs all connections to a configured address

	Instances of this class are mounted on a `requests.Session` as adapters for specific URL
	prefixes.

	Rather than using this class directly the easiest way to use it is with the `redirect`
	function.
	"""

	def __init__(self, destination: ipaddress.IPv4Address):
		super().__init__()
		self.destination = destination

	def get_connection(self, url: str, proxies: Mapping[str, str]|None = None) -> _HTTPConnectionPool:
		parts = urlparse(url)
		return _HTTPConnectionPool(parts.hostname, parts.port, address=self.destination)


class _HTTPConnectionPool(connectionpool.HTTPConnectionPool):

	class ConnectionCls(connection.HTTPConnection):

		# Undo the damage done by parent class which makes 'host' a property with magic
		host = ""

		def __init__(self, /, address: ipaddress.IPv4Address, **kwargs: Any):
			connection.HTTPConnection.__init__(self, **kwargs)
			self._dns_host = str(address)
