#!/bin/bash
#
# Copyright (c) 2019 Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

set -eu -o pipefail
shopt -s nullglob globstar extglob

enable -f /usr/lib/bash/head head
enable -f /usr/lib/bash/unlink unlink

declare -r DEFAULT_THEME=twentynineteen
declare -r WORKER_USER=www-data

declare DB_HOST DB_NAME DB_USER DB_PASS
declare HOME_URL SITE_URL
declare -a THEMES=( ${THEMES-} )
declare -a PLUGINS=( ${PLUGINS-} )
declare -a LANGUAGES=( ${LANGUAGES-} )
declare -a STATIC_PATTERNS=(
	${STATIC_PATTERNS-}
	"*.crt"
	"*.md"
	"*.[pm]o"
	"*.pot"
	"*.txt"
	"COPYING"
	"LICEN[CS]E"
	"README"
	"readme.html"
	"composer.*"
)
declare -a PHP_DIRECTIVES=(
	${PHP_DIRECTIVES-}
	upload_max_filesize=20M
	post_max_size=20M
)
declare -a WP_CONFIGS=(
	${WP_CONFIGS-}
	/etc/wordpress/*config.php
)


timestamp()
{
	echo "[$(date --utc +'%Y-%m-%dT%H:%M:%S%z')] $*"
}

create_config()
{
	[[ -f wp-config.php ]] && unlink wp-config.php

	local IFS=$'\n'
	sort -u <<-END_LIST |
		/usr/share/wordpress/wp-config.php
		${WP_CONFIGS[*]}
	END_LIST
	xargs cat |
	wp config create \
		--extra-php \
		--skip-check \
		--dbname="${DB_NAME? Please set DB_NAME in /etc/wordpress/}" \
		--dbuser="${DB_USER? Please set DB_USER in /etc/wordpress/}" \
		${DB_HOST+--dbhost="${DB_HOST}"} \
		${DB_PASS+--dbpass="${DB_PASS}"}

	local site_url=${SITE_URL? Please set SITE_URL}
	local site_path=${site_url##*://*([^/])}
	local home_url=${HOME_URL:-${site_url%$site_path}}

	wp config set WP_SITEURL "${site_url%/}"
	wp config set WP_HOME "${home_url%/}"
}

setup_database() {
	wp core is-installed && return

	local domain=${SITE_URL#*://}
	domain=${domain%%[:/]*}

	wp core install \
		--url="${SITE_URL%/}" \
		--title="${SITE_TITLE:-New Wordpress Site}" \
		--admin_user="${SITE_ADMIN:-admin}" \
		--admin_email="${SITE_ADMIN_EMAIL:-admin@$domain}" \
		${SITE_ADMIN_PASSWORD+--admin_password="${SITE_ADMIN_PASSWORD}"}

	# Start with a pretty, restful permalink structure, instead of the plain, 
	# ugly default. The user can change this as they please through the admin 
	# dashboard.
	wp rewrite structure /posts/%postname%
}

setup_s3() {
	# https://github.com/humanmade/S3-Uploads

	declare -a configs=( "${!S3_ENDPOINT_@}" )
	[[ ${#configs[*]} -gt 0 ]] || return 0

	[[ -v S3_UPLOADS_ENDPOINT ]] &&
	[[ -v S3_ENDPOINT_KEY ]] &&
	[[ -v S3_ENDPOINT_SECRET ]] ||
		return 0

	wp plugin activate s3-uploads

	[[ -v S3_UPLOADS_USE_LOCAL ]] &&
		wp config set S3_UPLOADS_USE_LOCAL true --raw

	wp config set S3_UPLOADS_BUCKET_URL "${S3_UPLOADS_ENDPOINT}"
	wp config set S3_UPLOADS_KEY ${S3_ENDPOINT_KEY}
	wp config set S3_UPLOADS_SECRET ${S3_ENDPOINT_SECRET} --quiet

	# Plugin requires something here, it's not used
	wp config set S3_UPLOADS_REGION ''

	# Due to what appears to be a bug in the plugin, this MUST be a non-empty
	# string; mostly it just affects the log output
	wp config set S3_UPLOADS_BUCKET "CONFIGURED-BUCKET"
}

setup_components() {
	setup_database

	# Update pre-installed components
	wp core update --minor
	wp plugin update --all
	wp theme update --all
	wp language core update
	wp language plugin update --all
	wp language theme update --all
	composer update --prefer-dist

	# Ensure at least one theme is installed
	[[ ${#THEMES[*]} -eq 0 ]] && THEMES+=( ${DEFAULT_THEME} )

	# Install configured components
	[[ ${#PLUGINS[*]} -gt 0 ]] && wp plugin install "${PLUGINS[@]}"
	[[ ${#THEMES[*]} -gt 0 ]] && wp theme install "${THEMES[@]}"
	[[ ${#LANGUAGES[*]} -gt 0 ]] && wp language core install "${LANGUAGES[@]}"
	[[ ${#LANGUAGES[*]} -gt 0 ]] && wp language plugin install --all "${LANGUAGES[@]}"
	[[ ${#LANGUAGES[*]} -gt 0 ]] && wp language theme install --all "${LANGUAGES[@]}"

	# Ensure a theme is active
	[[ $(wp theme list --status=active --format=count) -eq 0 ]] &&
		wp theme activate $(wp theme list --field=name | head -n1)

	setup_s3

	return 0
}

setup_media()
{
	# UID values change on every run, ensure the owner and group are set 
	# correctly on ./media
	chown -R $WORKER_USER:$WORKER_USER ./media
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
		--exclude=/static/ \
		--exclude=/media/ \
		--exclude=/vendor/ \
		--force \
		--info="${flags[*]}" \
		--times \
		--prune-empty-dirs \
		--recursive \
		--relative \
		--times \
		. static/
}

next_cron()
{
	echo $(($(wp cron event list --field=time|sort|head -n1) - $(date +%s)))
}

run_cron()
{
	enable -f /usr/lib/bash/sleep sleep
	enable -f /usr/lib/bash/head head
	while wp cron event run --due-now || true; do
		sleep $(next_cron)
		timestamp "Executing cron tasks"
	done
}

run_background_cron()
{ (
	export -f next_cron run_cron timestamp
	exec -a wp-cron /bin/bash <<<run_cron
)& }


for file in /etc/wordpress/**/*.conf; do
	source "${file}"
done

if [[ -e ${PLUGINS_LIST:=/etc/wordpress/plugins.txt} ]]; then
	PLUGINS+=( $(<"${PLUGINS_LIST}") )
fi
if [[ -e ${THEMES_LIST:=/etc/wordpress/themes.txt} ]]; then
	THEMES+=( $(<"${THEMES_LIST}") )
fi
if [[ -e ${LANGUAGES_LIST:=/etc/wordpress/languages.txt} ]]; then
	LANGUAGES+=( $(<"${LANGUAGES_LIST}") )
fi

declare -a extra_args

for directive in "${PHP_DIRECTIVES[@]}"; do
	extra_args+=( -d "${directive}" )
done

case "$1" in
	collect-static) create_config && setup_components && collect_static ;;
	run-cron) create_config && run_cron ;;
	php-fpm)
		timestamp "Starting Wordpress preparation"
		create_config
		setup_components
		setup_media
		collect_static
		timestamp "Completed Wordpress preparation"
		run_background_cron
		exec "$@" "${extra_args[@]}"
		;;
	*)
		[[ -v DB_NAME ]] && create_config
		exec "$@"
		;;
esac
