#!/bin/bash
set -eu
shopt -s nullglob globstar

declare -a THEMES=() PLUGINS=() LANGUAGES=()
declare DB_HOST DB_NAME DB_USER DB_PASS

create_config()
{
	wp config create \
		--extra-php \
		--skip-check \
		--dbhost="${DB_HOST? Please set DB_HOST in /etc/wordpress/}" \
		--dbname="${DB_NAME? Please set DB_NAME in /etc/wordpress/}" \
		${DB_USER+--dbuser=${DB_USER}} \
		${DB_PASS+--dbpass=${DB_PASS}} \
	<<-END_CONFIG
		define('DISALLOW_FILE_MODS', true);
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

	# Install configured components
	wp plugin install "${PLUGINS[@]}"
	wp theme install "${THEMES[@]}"
	wp language core install "${LANGUAGES[@]}"
	wp language plugin install --all "${LANGUAGES[@]}" || true
	wp language theme install --all "${LANGUAGES[@]}" || true

	find -name static -prune \
		-name uploads -prune \
		-o -type f -not -iname '*.php' \
		-exec install -vD '{}' 'static/{}' \;
}

for file in /etc/wordpress/*.conf /etc/wordpress/**/*.conf; do
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
	php-fpm)
		create_config
		setup
		exec "$@"
		;;
	*)
		[[ -v DB_HOST ]] && create_config || true
		exec "$@"
		;;
esac
