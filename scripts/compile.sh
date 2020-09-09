#!/bin/bash
set -eux

# Packaged build dependencies
BUILD_DEPS=(
	autoconf
	build-base
	gmp-dev
	imagemagick-dev
	jpeg-dev
	libpng-dev
	libzip-dev
)

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

# Install packaged dependencies
apk update
apk add "${BUILD_DEPS[@]}"

# Build & install distributed extensions
if php_version -gt 7.4; then
	GD_ARGS=( --with-jpeg=/usr )
else
	GD_ARGS=( --with-png-dir=/usr --with-jpeg-dir=/usr )
fi
docker-php-ext-configure gd "${GD_ARGS[@]}"
docker-php-ext-install -j$(nproc) "${PHP_EXT[@]}"

# Download, build & install the Image Magick extension
pecl install imagick
echo "extension=imagick.so" > /usr/local/etc/php/conf.d/imagick.ini
