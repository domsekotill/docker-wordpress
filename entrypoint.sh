#!/bin/bash
set -eu
shopt -s nullglob globstar

declare -a THEMES=() PLUGINS=() LANGUAGES=()
declare DB_HOST DB_NAME DB_USER DB_PASS
declare -a STATIC_PATTERNS=(
	"*.crt"
	"*.md"
	"*.[pm]o"
	"*.txt"
	"COPYING"
	"LICEN[CS]E"
	"README"
	"readme.html"
)

create_config()
{
	wp config create \
		--extra-php \
		--skip-check \
		--dbname="${DB_NAME? Please set DB_NAME in /etc/wordpress/}" \
		--dbuser="${DB_USER? Please set DB_USER in /etc/wordpress/}" \
		${DB_HOST+--dbhost=${DB_HOST}} \
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

collect_static()
{
	declare -a args=()
	for pattern in "${STATIC_PATTERNS[@]}"; do
		args+=(-o -iname "$pattern")
	done
	find -name static -prune \
		-o -name uploads -prune \
		-o -type f -not \( -iname '*.php' "${args[@]}" \) \
		-exec install -vD '{}' 'static/{}' \;
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
	collect-static) create_config && collect_static ;;
	php-fpm)
		create_config
		setup
		collect_static
		exec "$@"
		;;
	*)
		[[ -v DB_NAME ]] && create_config || true
		exec "$@"
		;;
esac
