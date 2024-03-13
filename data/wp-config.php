// <?php

/****
 * Additional configurations required by the docker image
 ****/

/**
 * Disable running wp-cron.php on every page load. A sidecar process
 * examines the status of cron jobs and handles scheduling and running them.
 **/
define('DISABLE_WP_CRON', true);

/**
 * Move the uploads volume/directory into the top of the Wordpress
 * installation.
 **/
define('UPLOADS', 'media');

/**
 * Disable script concatenation in the admin interface.
 * This puts extra load on the PHP server that Nginx should be taking.
 * The benefits of concatenation should be negated when using HTTP/2.
 **/
define('CONCATENATE_SCRIPTS', false);

/**
 * Log all errors, warnings and info log lines to STDOUT
 */
define('WP_DEBUG_LOG', '/dev/stdout');

/**
 * Stop the site-health tool from complaining about unwritable filesystems.
 * Background upgrades are performed by a user with write privileges via the
 * wp-cli tool.
 **/
if ( !defined( 'WP_CLI' ) ):
define('FTP_USER', 'nemo');
define('FTP_PASS', '****');
endif;

/**
 * Run the Composer autoloader, if available
 * Assume the CWD is always /app and vendor is always in it.
 **/
if ( is_file(__DIR__ . '/vendor/autoload.php') )
	require_once __DIR__ . '/vendor/autoload.php';
