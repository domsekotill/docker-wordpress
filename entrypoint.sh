#!/bin/bash
set -eu -o pipefail
shopt -s nullglob globstar

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
	if [[ ! -e wp-config.php ]]; then
		:
	elif [[ x${1-} = x-f ]]; then
		rm wp-config.php
	else
		return 0
	fi
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
	wp theme activate $(wp theme list --field=name | head -n1)
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
		--exclude=wp-content/uploads/ \
		--force \
		--info="${flags[*]}" \
		--noatime \
		--recursive \
		--relative \
		--times \
		. static/
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
