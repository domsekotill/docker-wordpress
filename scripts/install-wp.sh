#!/bin/bash
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
