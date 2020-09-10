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
if ( is_file(ABSPATH . 'vendor/autoload.php') )
	require_once ABSPATH . 'vendor/autoload.php';
