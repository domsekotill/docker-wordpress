// <?php

// Serves the word "eggs" at /eggs
// Used for checking that this file has been loaded correctly

if ( !defined('WP_CLI') && $_SERVER['REQUEST_URI'] == '/eggs' ) {
	echo("eggs");
	exit;
}
