#!/bin/bash
set -eu
shopt -s nullglob globstar

create_config()
{
	wp config create \
		--extra-php \
		--skip-check \
		--dbhost="${DB_HOST? Please set DB_HOST in /etc/wordpress/}" \
		--dbname="${DB_NAME? Please set DB_NAME in /etc/wordpress/}" \
		--dbuser="${DB_USER? Please set DB_USER in /etc/wordpress/}" \
		--dbpass="${DB_PASSWORD? Please set DB_PASSWORD in /etc/wordpress/}" \
	<<-END_CONFIG
		define('DISALLOW_FILE_MODS', true);
	END_CONFIG
}

setup() {
	wp core update --minor
	wp plugin install "${PLUGINS[@]}"
	wp theme install "${THEMES[@]}"
	wp language core update
	wp language plugin update --all
	wp language theme update --all

	find -name static -prune \
		-o -type f -not -iname '*.php' \
		-exec install -vD '{}' 'static/{}' \;
}

declare -a THEMES=( sela /pkg/sela-child.zip )
declare -a PLUGINS

for file in /etc/wordpress/*.conf /etc/wordpress/**/*.conf; do
	source ${file}
done

if [[ -e ${PLUGINS_LIST:=/etc/wordpress/plugins.txt} ]]; then
	PLUGINS+=( $(<${PLUGINS_LIST}) )
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
