#  Copyright 2024  Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Fixtures for S3 services
"""

from __future__ import annotations

import atexit
import json
from collections.abc import Iterator
from gzip import GzipFile
from pathlib import Path
from typing import ClassVar
from typing import TypeAlias
from uuid import NAMESPACE_URL
from uuid import uuid3

from behave import fixture
from behave.runner import Context
from behave_utils import URL
from behave_utils.binaries import DownloadableExecutable
from behave_utils.docker import Cli
from behave_utils.docker import Container
from behave_utils.docker import Image
from behave_utils.docker import Network
from behave_utils.secret import make_secret
from behave_utils.utils import wait
from requests import Session
from typing_extensions import Self
from wp import Site

BucketsKey: TypeAlias = tuple[str, bool]

CURRENT_BUCKET_KEY: BucketsKey = "current://", True

MINIO_IMAGE = Image.pull(f"quay.io/minio/minio:latest")

__all__ = [
	"Bucket",
	"Minio",
	"bucket_fixture",
	"current_bucket_fixture",
]


class DownloadableMC(DownloadableExecutable, name="minio-client"):

	def get_latest(self, session: Session) -> str:
		return "latest"

	def get_stream(self, session: Session, version: str) -> GzipFile:
		binary = "mc.exe" if self.kernel == "windows" else "mc"
		url = f"https://dl.min.io/client/mc/release/{self.kernel}-{self.goarch}/{binary}"
		resp = session.get(url, allow_redirects=True, stream=True)
		assert resp.raw is not None
		return GzipFile(fileobj=resp.raw)


class Minio(Container):
	"""
	A `Container` subclass to run and manage a Minio S3 service
	"""

	_inst: ClassVar[Minio|None] = None

	domain = "s3.test.local"

	@classmethod
	def get_running(cls) -> Minio:
		"""
		Return a running instance of the Minio server
		"""
		if not (self := cls._inst):
			self = cls._inst = Minio()
			self.start()
		return self

	def __init__(self) -> None:
		self.key = make_secret(8)
		self.secret = make_secret(20)

		mc_bin = DownloadableMC("latest").get_binary()
		Container.__init__(
			self, MINIO_IMAGE,
			["server", "/tmp", "--address=:80", "--console-address=:9001"],
			volumes=[(mc_bin, Path("/bin/mc"))],
			env=dict(
				MINIO_ROOT_USER=self.key,
				MINIO_ROOT_PASSWORD=self.secret,
				MINIO_DOMAIN=self.domain,
			),
		)
		self.mc = Cli(self, "/bin/mc")

	def start(self) -> None:
		"""
		Idempotently start the service, and register an alias to it with the *mc* tool
		"""
		if self.is_running():
			return
		super().start()
		atexit.register(self.stop, rm=True)
		wait(lambda: self.is_running())
		# Add "local" alias
		self.mc("config", "host", "add", "local", "http://localhost", self.key, self.secret)

	def bucket_domain(self, bucket: str, use_subdomain: bool) -> str:
		"""
		Return the domain name to use for a given bucket

		If 'use_subdomain' is `True` the name will consist of the bucket name as a subdomain
		of the server domain, otherwise it be the same as the server' domain.
		"""
		return f"{bucket}.{self.domain}" if use_subdomain else f"{self.domain}"

	def bucket_url(self, bucket: str, use_subdomain: bool) -> URL:
		"""
		Return the HTTP endpoint URL to use for the given bucket

		The URL will have the domain as returned by `Minio.bucket_domain`, with the bucket
		name as the only path component if 'use_subdomain' is `False`.
		"""
		domain = self.bucket_domain(bucket, use_subdomain)
		base = URL(f"http://{domain}")
		return base if use_subdomain else (base / bucket)

	def add_bucket_user(self, bucket: str, key: str, secret: str) -> None:
		"""
		Create an ephemeral bucket and account with access to that bucket
		"""
		policy = f"{bucket}-write"
		stmt = json.dumps(
			dict(
				Version="2012-10-17",
				Statement=[
					dict(
						Effect="Allow",
						Action=["s3:ListBucket"],
						Resource=[f"arn:aws:s3:::{bucket}"],
					),
					dict(
						Effect="Allow",
						Action=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
						Resource=[f"arn:aws:s3:::{bucket}/*"],
					),
				],
			),
		)
		self.mc("mb", f"local/{bucket}")
		self.mc("admin", "user", "add", "local", key, secret)
		self.mc("admin", "policy", "create", "local", policy, "/dev/stdin", input=stmt)
		self.mc("admin", "policy", "attach", "local", policy, "--user", key)

	def rm_bucket_user(self, bucket: str, key: str) -> None:
		"""
		Remove an ephemeral bucket and user
		"""
		self.mc("admin", "user", "rm", "local", key)
		self.mc("rb", f"local/{bucket}", "--force")

	def has_path(self, bucket: str, path: Path) -> bool:
		"""
		Return whether the given path (key) exists in the named bucket
		"""
		res = self.mc("stat", f"local/{bucket}/{path}", query=True)
		# import time
		# time.sleep(3600)
		return res == 0


class Bucket:
	"""
	An ephemeral bucket fixture within an S3 service

	To create the bucket on the server and update name records, an instance must be used as
	a context manager.  Once the context ends, the bucket is removed.
	"""

	def __init__(
		self,
		ident: str,
		use_subdomain: bool,
		network: Network,
		server: Minio|None = None,
	):
		self.network = network
		self.server = server or Minio.get_running()

		self.name = str(uuid3(NAMESPACE_URL, ident))
		self.domain = self.server.bucket_domain(self.name, use_subdomain)
		self.url = self.server.bucket_url(self.name, use_subdomain)
		self.key = make_secret(8)
		self.secret = make_secret(20)

	def __enter__(self) -> Self:
		self.server.start() # Ensure server is started, method is idempotent
		self.server.add_bucket_user(self.name, self.key, self.secret)
		self.server.connect(self.network, self.domain)
		return self

	def __exit__(self, *_: object) -> None:
		self.server.rm_bucket_user(self.name, self.key)
		self.server.disconnect(self.network, self.domain)

	def has_path(self, path: Path) -> bool:
		"""
		Return whether the given path (key) exists in this bucket
		"""
		return self.server.has_path(self.name, path)


@fixture
def bucket_fixture(context: Context, /, site: Site, use_subdomain: bool) -> Iterator[Bucket]:
	"""
	When used with `use_fixture`, creates and returns a `Bucket` fixture

	The 'use_subdomain' parameter selects which type of bucket addressing is used, out of
	subdomain or path-based buckets.
	"""
	buckets = _buckets_from_context(context)
	key: BucketsKey = site.url, use_subdomain
	if (bucket := buckets.get(key)):
		yield bucket
		return
	prev = buckets.get(CURRENT_BUCKET_KEY, None)
	with Bucket(site.url, use_subdomain, site.network) as bucket:
		buckets[key] = buckets[CURRENT_BUCKET_KEY] = bucket
		yield bucket
	del buckets[key]
	if prev:
		buckets[CURRENT_BUCKET_KEY] = prev
	else:
		del buckets[CURRENT_BUCKET_KEY]


@fixture
def current_bucket_fixture(context: Context) -> Iterator[Bucket]:
	"""
	When used with `use_fixture`, returns the most recently created `Bucket` fixture
	"""
	buckets = _buckets_from_context(context)
	yield buckets[CURRENT_BUCKET_KEY]


def _buckets_from_context(context: Context) -> dict[BucketsKey, Bucket]:
	if not hasattr(context, "buckets"):
		context.buckets = dict[BucketsKey, Bucket]()
	assert isinstance(context.buckets, dict)
	return context.buckets
