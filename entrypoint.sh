#!/bin/bash
set -eu

# constants
WP_ROOT=${WORDPRESS_ROOT:-/var/www/html}
WP_CONTENT=${WP_ROOT}/wp-content
WP_CONFIG=${WP_ROOT}/wp-config.php
MYSQL_CONF=/etc/wordpress/mysql.conf
SECRET_CONF=/etc/wordpress/secret.conf

genkey() { head -c${1:-1M} /dev/urandom | sha1sum | cut -d' ' -f1; }

create_config()
{
	run_setup_secret
	source ${MYSQL_CONF}
	source ${SECRET_CONF}
	cat > $WP_CONFIG <<-END_CONFIG
		<?php
		/**
		 * Generated by entrypoint.sh
		 * `date`
		 */

		define('DB_HOST', '${DB_HOST}');
		define('DB_NAME', '${DB_NAME}');
		define('DB_USER', '${DB_USER}');
		define('DB_PASSWORD', '${DB_PASSWORD}');

		define('DB_CHARSET', 'utf8');
		define('DB_COLLATE', '');

		\$table_prefix = 'wp_';

		define('AUTH_KEY',         '${AUTH_KEY}');
		define('SECURE_AUTH_KEY',  '${SECURE_AUTH_KEY}');
		define('LOGGED_IN_KEY',    '${LOGGED_IN_KEY}');
		define('NONCE_KEY',        '${NONCE_KEY}');
		define('AUTH_SALT',        '`genkey 128`');
		define('SECURE_AUTH_SALT', '`genkey 128`');
		define('LOGGED_IN_SALT',   '`genkey 128`');
		define('NONCE_SALT',       '`genkey 128`');

		define('FS_METHOD', 'direct');

		define('WP_DEBUG', false);
		if ( !defined('ABSPATH') )
			define('ABSPATH', dirname(__FILE__) . '/');

		require_once(ABSPATH . 'wp-settings.php');
	END_CONFIG
}

run_setup()
{
	# setup entrypoint
	# ----------------
	# Setup the database, install the scripts & make a config

	if [ -e ${MYSQL_CONF} ]; then
		source ${MYSQL_CONF}
	fi

	# parse command line arguments
	SHIFT=shift
	POP='"$2"; SHIFT=shift; shift'
	while [ $# -gt 0 ]; do
		case "$1" in
			--*=*)
				set ${1%%=*} ${1#*=} "${@:2}"
				continue
				;;
			-*)
				set ${1:0:2} ${1#??} "${@:2}"
				# SHIFT adds the character-option hyphen onto $2 if is not POPed
				# as an argument first.
				SHIFT='set -$2 "${@:3}"; SHIFT=shift'
				continue
				;;

			-c|--clear) unset DB_HOST DB_NAME DB_USER DB_PASSWORD ;;
			-h|--host) eval ARG_HOST=$POP ;;
			-d|--database) eval ARG_NAME=$POP ;;
			-u|--user) eval ARG_USER=$POP ;;
			-p|--password) eval ARG_PASSWORD=$POP ;;
		esac
		$SHIFT
	done

	# command line argument defaults
	: ${ARG_HOST:=${DB_HOST:-mysql}}
	: ${ARG_NAME:=${DB_NAME?A database name is required}}
	: ${ARG_USER:=${DB_USER:-${ARG_NAME}_user}}
	: ${ARG_PASSWORD:=${DB_PASSWORD:-}}

	cat >${MYSQL_CONF} <<-END
		DB_HOST=${ARG_HOST}
		DB_NAME=${ARG_NAME}
		DB_USER=${ARG_USER}
		DB_PASSWORD=${ARG_PASSWORD}
	END
}

run_setup_secret()
{
	if [ -e ${SECRET_CONF} ]; then
		return
	fi

	local key=$(genkey)

	cat >${SECRET_CONF} <<-END
		AUTH_KEY="${key}"
		SECURE_AUTH_KEY="${key}"
		LOGGED_IN_KEY="${key}"
		NONCE_KEY="${key}"
	END
}

update_all() {
	wp core update --minor
	wp plugin update --all
	wp theme update --all
	wp language core update
	wp language plugin update --all
	wp language theme update --all

	find -name wp-content -prune -o -type f -not -iname '*.php' \
		-exec install -vD '{}' 'static/{}' \;
}

case "$1" in
	setup)
		shift
		run_setup "$@"
		run_setup_secret
		;;
	php-fpm)
		create_config
		update_all
		exec "$@"
		;;
	*)
		[ -e ${MYSQL_CONF} ] && create_config || true
		exec "$@"
		;;
esac
