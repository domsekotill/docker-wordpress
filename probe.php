<?php
/**
 * Plugin Name: Liveness probe
 * Description: Responds to requests to /.probe with an HTTP code indicating the
 *              status of the app
 * Licence: MPL-2.0
 * Author: Dominik Sekotill
 */


if ( parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) == '/.probe' ):

add_filter('option_active_plugins', function( $plugins ) { return array(); });
add_action('setup_theme', function() { exit(200); });

endif;
