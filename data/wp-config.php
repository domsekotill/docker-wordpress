// <?php

/****
 * Additional configurations required by the docker image
 ****/

/**
 * Plugins, themes and language packs cannot be configured through the admin 
 * interface; modify the configuration in /etc/wordpress/ according to the 
 * documentation for PLUGINS[_LIST], THEMES[_LIST] and LANGUAGES[_LIST]
 **/
define('DISALLOW_FILE_MODS', true);

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
