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
 * Run the Composer autoloader, if available
 * Assume the CWD is always /app and vendor is always in it.
 **/
if ( is_file(ABSPATH . 'vendor/autoload.php') )
	require_once ABSPATH . 'vendor/autoload.php';
