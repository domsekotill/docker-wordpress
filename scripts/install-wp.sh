#!/bin/bash
set -eux

WP_PASSWORD_HASH=https://raw.githubusercontent.com/Ayesh/WordPress-Password-Hash/1.5.1

# Install Wordpress core
wp core download --skip-content --locale=en_GB --version=$1

# Clear away template PHP clutter
rm wp-config-sample.php

# Ensure needed directories are made with the correct permissions
mkdir --mode=go+w media
mkdir -p wp-content/mu-plugins

# Install non-optional plugins
curl ${WP_PASSWORD_HASH}/wp-php-password-hash.php \
	>wp-content/mu-plugins/password-hash.php
