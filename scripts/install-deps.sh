#!/bin/sh
set -eux

# Install packaged dependencies
apk update
apk add \
	bash \
	imagemagick-libs \
	libgmpxx \
	libjpeg \
	libpng \
	libwebp \
	libzip \
	rsync \
