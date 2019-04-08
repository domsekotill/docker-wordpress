#!/bin/sh
set -eu

die() { echo "$*"; exit 1; }

VERSION="$1"
SHA1="$2"
URL="https://wordpress.org/wordpress-${VERSION}.tar.gz"

# check user has not attempted to override WORDPRESS_VERSION
test "$VERSION" = "$WORDPRESS_VERSION" ||
	die 'Use --build-arg="version=[...]" to set the wordpress version'

# get a hash if not passed in
if [ -z "$SHA1" ]; then
	SHA1="$(curl -sSL "${URL}.sha1")"
fi

curl -o wordpress.tar.gz -SL "$URL"

# check hash if available
if [ -n "$SHA1" ]; then
	echo "${SHA1} *wordpress.tar.gz" | sha1sum -c - ||
		die "Hash does not match, maybe there was a download error?"
fi

# unpack source
tar -xzf wordpress.tar.gz -C /usr/src/ &&
	rm wordpress.tar.gz
