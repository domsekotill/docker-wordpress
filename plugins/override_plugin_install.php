<?php
/**
 * Plugin Name: Disable New Plugins
 * Plugin URI: https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/tree/master/plugins
 * Description: Removes the "Add Plugin" button from the admin dashboard
 * Licence: MPL-2.0
 * Licence URI: https://www.mozilla.org/en-US/MPL/2.0/
 * Author: Dominik Sekotill
 * Author URI: https://code.kodo.org.uk/dom
 */

add_filter( 'user_has_cap', 'override_plugin_install', 10, 3 );

function override_plugin_install( $allcaps, $caps, $args ) {
	if ( 'install_plugins' == $args[0] ) {
		$allcaps[$caps[0]] = false;
	}
	return $allcaps;
}
