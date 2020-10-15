<?php
/**
 * Plugin Name: File Modification Blocker
 * Plugin URI: https://wordpress.stackexchange.com/a/300718
 * Description: Block file modification except for security updates.
 * Licence: CC BY-SA 3.0
 * Licence URI: https://creativecommons.org/licenses/by-sa/3.0/
 * Author: Marc Guay
 * Author URI: https://wordpress.stackexchange.com/users/69982/marcguay
 */

add_filter( 'file_mod_allowed', 'override_file_mod_allowed', 10, 2 );

function override_file_mod_allowed( $setting, $context ) {
	if ( $context == 'automatic_updater' ) {
		return true;
	}
	return $setting;
}
