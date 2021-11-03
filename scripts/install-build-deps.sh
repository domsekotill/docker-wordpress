#!/bin/sh
# Copyright 2019-2021 Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -eux

# Install packaged dependencies
apk update
apk add \
	autoconf \
	build-base \
	gmp-dev \
	imagemagick-dev \
	jpeg-dev \
	libpng-dev \
	libwebp-dev \
	libzip-dev \
