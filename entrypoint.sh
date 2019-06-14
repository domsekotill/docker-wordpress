#!/bin/bash
#
# Copyright (c) 2019 Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

set -eu -o pipefail
shopt -s nullglob globstar
enable -f /usr/lib/bash/sleep sleep

declare -a THEMES=() PLUGINS=() LANGUAGES=()
declare DB_HOST DB_NAME DB_USER DB_PASS
declare -a STATIC_PATTERNS=(
	"*.crt"
	"*.md"
	"*.[pm]o"
	"*.pot"
	"*.txt"
	"COPYING"
	"LICEN[CS]E"
	"README"
	"readme.html"
)

create_config()
{
	local IFS=$'\n'
	local additional_config

	if [[ ! -e wp-config.php ]]; then
		:
	elif [[ x${1-} = x-f ]]; then
		rm wp-config.php
	else
		return 0
	fi

	[[ ${WP_CONFIG_EXTRA:=/etc/wordpress/wp-config-extra.php} =~ ^/ ]] ||
		WP_CONFIG_EXTRA=/etc/wordpress/${WP_CONFIG_EXTRA}
	[[ -r ${WP_CONFIG_EXTRA} ]] &&
		additional_config=${WP_CONFIG_EXTRA}

	wp config create \
		--extra-php \
		--skip-check \
		--dbname="${DB_NAME? Please set DB_NAME in /etc/wordpress/}" \
		--dbuser="${DB_USER? Please set DB_USER in /etc/wordpress/}" \
		${DB_HOST+--dbhost=${DB_HOST}} \
		${DB_PASS+--dbpass=${DB_PASS}} \
	<<-END_CONFIG
		/*
		 * Plugins, themes and language packs cannot be configured through the 
		 * admin interface; modify the configuration in /etc/wordpress/ 
		 * according to the documentation for PLUGINS[_LIST], THEMES[_LIST] and 
		 * LANGUAGES[_LIST]
		 */
		define('DISALLOW_FILE_MODS', true);

		/*
		 * Disable running wp-cron.php on every page load.
		 * Instead corn jobs will be run every 15 minutes.
		 */
		define('DISABLE_WP_CRON', true);

		/*
		 * Move the uploads volume/directory into the top of the Wordpress 
		 * installation.
		 */
		define('UPLOADS', 'media');

		/* BEGIN WP_CONFIG_LINES */
		${WP_CONFIG_LINES[*]}
		/* END WP_CONFIG_LINES */

		/* BEGIN ${WP_CONFIG_EXTRA} */
		${additional_config+$(<$additional_config)}
		/* END ${WP_CONFIG_EXTRA} */
	END_CONFIG
}

setup() {
	# Update pre-installed components
	wp core update --minor
	wp plugin update --all
	wp theme update --all
	wp language core update
	wp language plugin update --all
	wp language theme update --all

	# Install required components
	wp plugin install --activate password-hash

	# Install configured components
	[[ ${#PLUGINS[*]} -gt 0 ]] && wp plugin install "${PLUGINS[@]}"
	[[ ${#THEMES[*]} -gt 0 ]] && wp theme install "${THEMES[@]}"
	[[ ${#LANGUAGES[*]} -gt 0 ]] && wp language core install "${LANGUAGES[@]}"
	[[ ${#LANGUAGES[*]} -gt 0 ]] && wp language plugin install --all "${LANGUAGES[@]}"
	[[ ${#LANGUAGES[*]} -gt 0 ]] && wp language theme install --all "${LANGUAGES[@]}"

	[[ ${#THEMES[*]} -gt 0 ]] &&
	[[ $(wp theme list --status=active --format=count) -eq 0 ]] &&
	wp theme activate $(wp theme list --field=name | head -n1) ||
	true
}

collect_static()
{
	local IFS=,
	declare -a flags=(flist stats remove del)
	test -t 1 && flags+=(progress2)
	printf -- '- %s\n' "${STATIC_PATTERNS[@]}" |
	rsync \
		--checksum \
		--delete-delay \
		--exclude-from=- \
		--exclude='*.php' \
		--exclude=static/ \
		--exclude=media/ \
		--force \
		--info="${flags[*]}" \
		--noatime \
		--recursive \
		--relative \
		--times \
		. static/
}

run_cron()
{
	local interval=60
	while sleep $(wp cron schedule list --field=interval | head -n1); do
		wp cron event run --due-now
	done
}

for file in /etc/wordpress/**/*.conf; do
	source ${file}
done

if [[ -e ${PLUGINS_LIST:=/etc/wordpress/plugins.txt} ]]; then
	PLUGINS+=( $(<${PLUGINS_LIST}) )
fi
if [[ -e ${THEMES_LIST:=/etc/wordpress/themes.txt} ]]; then
	THEMES+=( $(<${THEMES_LIST}) )
fi
if [[ -e ${LANGUAGES_LIST:=/etc/wordpress/languages.txt} ]]; then
	LANGUAGES+=( $(<${LANGUAGES_LIST}) )
fi

case "$1" in
	database-setup) create_config -f && wp core install "${@:2}" ;;
	install-setup) create_config && setup ;;
	collect-static) create_config && collect_static ;;
	run-cron) create_config && run_cron ;;
	php-fpm)
		create_config
		setup
		collect_static
		run_cron &
		exec "$@"
		;;
	*)
		[[ -v DB_NAME ]] && create_config || true
		exec "$@"
		;;
esac
