#!/bin/bash
#
# Copyright 2019-2024 Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

set -eu -o pipefail
shopt -s nullglob globstar extglob

enable -f /usr/lib/bash/head head
enable -f /usr/lib/bash/unlink unlink

declare -r DEFAULT_THEME=twentytwentytwo
declare -r WORKER_USER=www-data
declare -r CONFIG_DIR=/etc/wordpress
declare -r WORK_DIR=${PWD}

declare DB_HOST DB_NAME DB_USER DB_PASS
declare HOME_URL SITE_URL
declare -a THEMES=( ${THEMES-} )
declare -a PLUGINS=( ${PLUGINS-} )
declare -a LANGUAGES=( ${LANGUAGES-} )
declare -a STATIC_PATTERNS=(
	${STATIC_PATTERNS-}
	".*"
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
	${WP_CONFIGS-${CONFIG_DIR}/**/*config.php}
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
		--dbname="${DB_NAME? Please set DB_NAME in ${CONFIG_DIR}/}" \
		--dbuser="${DB_USER? Please set DB_USER in ${CONFIG_DIR}/}" \
		${DB_HOST+--dbhost="${DB_HOST}"} \
		${DB_PASS+--dbpass="${DB_PASS}"}

	# Clear potentialy sensitive information from environment lest it leaks
	unset ${!DB_*}

	local site_url=${SITE_URL? Please set SITE_URL}
	local site_path=${site_url##*://*([^/])}
	local home_url=${HOME_URL:-${site_url%$site_path}}

	wp config set WP_SITEURL "${site_url%/}"
	wp config set WP_HOME "${home_url%/}"

	wp config set WP_DEBUG_LOG /dev/stdout;
}

setup_database() {
	local domain=${SITE_URL#*://}
	domain=${domain%%[:/]*}

	local admin_name=${SITE_ADMIN:-admin}
	local admin_email=${SITE_ADMIN_EMAIL:-admin@$domain}
	local admin_password=${SITE_ADMIN_PASSWORD-}

	# Clear potentialy sensitive information from environment lest it leaks
	unset ${!SITE_ADMIN*}

	wp core is-installed && return

	wp core install \
		--url="${SITE_URL%/}" \
		--title="${SITE_TITLE:-New Wordpress Site}" \
		--admin_user="${admin_name}" \
		--admin_email="${admin_email}" \
		${admin_password:+--admin_password="${admin_password}"}

	# Start with a pretty, restful permalink structure, instead of the plain,
	# ugly default. The user can change this as they please through the admin
	# dashboard.
	wp rewrite structure /posts/%postname%
}

setup_s3() {
	# https://github.com/humanmade/S3-Uploads

	[[ -v S3_MEDIA_ENDPOINT ]] &&
	[[ -v S3_MEDIA_KEY ]] &&
	[[ -v S3_MEDIA_SECRET ]] ||
		return 0

	wp config set S3_UPLOADS_BUCKET_URL "${S3_MEDIA_REWRITE_URL-$S3_MEDIA_ENDPOINT}"

	wp config set S3_MEDIA_ENDPOINT "${S3_MEDIA_ENDPOINT}"
	wp config set S3_UPLOADS_KEY "${S3_MEDIA_KEY}"
	wp config set S3_UPLOADS_SECRET "${S3_MEDIA_SECRET}" --quiet

	# Plugin requires something here, it's not used
	wp config set S3_UPLOADS_REGION 'eu-west-1'

	wp config set S3_UPLOADS_BUCKET "media-bucket"

	# If there is anything in ./media, upload it
	local contents=( media/* )
	[[ ${#contents[*]} -gt 0 ]] &&
		wp s3-uploads upload-directory media

	# Clear potentialy sensitive information from environment lest it leaks
	unset ${!S3_MEDIA_*}
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

	deactivate_missing_plugins

	setup_s3

	return 0
}

get_media_dir()
{
	[[ -v MEDIA ]] && return
	MEDIA=$(
		wp config get UPLOADS --type=constant ||
		wp option get upload_path
	)
	[[ -n "${MEDIA}" ]] && return
	local _wp_content=$(wp config get WP_CONTENT_DIR --type=constant)
	MEDIA=${_wp_content:-wp-content}/uploads
}

setup_media()
{
	# UID values change on every run, ensure the owner and group are set
	# correctly on the media directory/volume.
	get_media_dir
	chown -R ${WORKER_USER}:${WORKER_USER} "${MEDIA}"
}

collect_static()
{
	get_media_dir
	local IFS=,
	declare -a flags=(flist stats remove del)
	test -t 1 && flags+=(progress2)
	printf -- '- %s\n' "${STATIC_PATTERNS[@]}" |
	rsync \
		--checksum \
		--delete-delay \
		--exclude-from=- \
		--exclude='*.php' \
		--exclude="${MEDIA}" \
		--exclude=/static/ \
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

generate_static()
{
	mkdir -p static/errors
	wp eval 'get_template_part("404");' >static/errors/404.html
}

deactivate_missing_plugins()
{
	# Output active plugin entrypoints as a JSON array
	wp option get active_plugins --format=json |

	# Convert to lines of raw strings
	jq -r '.[]' |

	# Filter out plugin entrypoints that don't exist in wp-content/plugins
	while read plugin; do
		test -e wp-content/plugins/$plugin &&
			echo $plugin ||
			echo >&2 "Deactivating removed plugin: $(dirname $plugin)"
	done |

	# Convert raw lines back into a JSON array
	jq -nR '[inputs]' |

	# Update the active plugin entrypoints
	wp option update active_plugins --format=json
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


mkdir -p ${CONFIG_DIR}
cd ${CONFIG_DIR}
for file in **/*.conf; do
	source "${file}"
done

if [[ -e ${PLUGINS_LIST:=${CONFIG_DIR}/plugins.txt} ]]; then
	PLUGINS+=( $(<"${PLUGINS_LIST}") )
fi
if [[ -e ${THEMES_LIST:=${CONFIG_DIR}/themes.txt} ]]; then
	THEMES+=( $(<"${THEMES_LIST}") )
fi
if [[ -e ${LANGUAGES_LIST:=${CONFIG_DIR}/languages.txt} ]]; then
	LANGUAGES+=( $(<"${LANGUAGES_LIST}") )
fi

declare -a extra_args

for directive in "${PHP_DIRECTIVES[@]}"; do
	extra_args+=( -d "${directive}" )
done

cd ${WORK_DIR}
case "$1" in
	collect-static) create_config && setup_components && collect_static ;;
	run-cron) create_config && run_cron ;;
	php-fpm)
		timestamp "Starting Wordpress preparation"
		create_config
		setup_components
		setup_media
		collect_static
		generate_static
		timestamp "Completed Wordpress preparation"
		run_background_cron
		exec "$@" "${extra_args[@]}"
		;;
	*)
		[[ -v DB_NAME ]] && create_config
		exec "$@"
		;;
esac
