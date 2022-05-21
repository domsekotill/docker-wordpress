#!/bin/sh
set -eux

# Install packaged dependencies
apk update
apk add \
	bash \
	imagemagick-libs \
	jq \
	libgmpxx \
	libgomp \
	libjpeg \
	libpng \
	libwebp \
	libzip \
	rsync \
