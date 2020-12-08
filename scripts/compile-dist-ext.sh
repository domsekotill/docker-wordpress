#!/bin/bash
set -eux

# Distributed extensions
PHP_EXT=(
	bcmath
	exif
	gd
	gmp
	mysqli
	opcache
	sockets
	zip
)

php_version() {
	php -r "version_compare(PHP_VERSION, '$2', '${1#-}') or exit(1);" ||
		return 1
}

# Build & install distributed extensions
if php_version -gt 7.4; then
	GD_ARGS=( --with-jpeg=/usr --with-webp=/usr )
else
	GD_ARGS=( --with-png-dir=/usr --with-jpeg-dir=/usr --with-webp-dir=/usr )
fi
docker-php-ext-configure gd "${GD_ARGS[@]}"
docker-php-ext-install -j$(nproc) "${PHP_EXT[@]}"
