<?php
/**
 * Plugin Name: Disable Plugins & Theme Management
 * Plugin URI: https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/tree/master/plugins
 * Description: Prevents changes to installed code from the admin dashboard.  All such changes should be managed through deployment configuration.
 * Licence: MPL-2.0
 * Licence URI: https://www.mozilla.org/en-US/MPL/2.0/
 * Author: Dominik Sekotill
 * Author URI: https://code.kodo.org.uk/dom
 */

add_filter( 'user_has_cap', 'override_plugin_install', 10, 3 );

function override_plugin_install( $allcaps, $caps, $args ) {
	switch ($args[0]) {
	case 'delete_plugins':
	case 'delete_themes':
	case 'edit_plugins':
	case 'edit_themes':
	case 'install_plugins':
	case 'install_themes':
	case 'update_plugins':
	case 'update_themes':
		$allcaps[$caps[0]] = false;
	}
	return $allcaps;
}
