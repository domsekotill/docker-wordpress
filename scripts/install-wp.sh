#!/bin/bash
# Copyright 2019-2021 Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -eux

COMPOSER_INSTALLER_URL=https://getcomposer.org/installer
WP_CLI_URL=https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar

# Install Composer
curl -sSL ${COMPOSER_INSTALLER_URL} |
	php -- --install-dir=/usr/local/lib --filename=composer.phar
ln -s ../lib/composer.phar /usr/local/bin/composer

# Install WP-CLI
curl -sSL ${WP_CLI_URL} \
    >/usr/local/lib/wp-cli.phar

# Install Wordpress core
wp core download --skip-content --locale=en_GB --version=$1

# Clear away template PHP clutter
rm wp-config-sample.php

# Ensure needed directories are made with the correct permissions
mkdir --mode=go+w media
mkdir -p wp-content/mu-plugins

# Install composer managed dependencies
export COMPOSER_ALLOW_SUPERUSER=1
composer install --prefer-dist
