#!/bin/sh
set -eux

# Install packaged dependencies
apk update
apk add \
	autoconf \
	build-base \
	git \
	gmp-dev \
	imagemagick-dev \
	jpeg-dev \
	libpng-dev \
	libwebp-dev \
	libzip-dev \
