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

# Install packaged dependencies
apk update
apk add "${BUILD_DEPS[@]}"

# Build & install distributed extensions
docker-php-ext-configure gd --with-png-dir=/usr --with-jpeg-dir=/usr
docker-php-ext-install -j$(nproc) "${PHP_EXT[@]}"

# Download, build & install the Image Magick extension
pecl install imagick
echo "extension=imagick.so" > /usr/local/etc/php/conf.d/imagick.ini
