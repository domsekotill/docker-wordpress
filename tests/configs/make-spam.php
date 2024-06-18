// <?php

// Serves the word "spam" at /spam
// Used for checking that this file has been loaded correctly

if ( !defined('WP_CLI') && $_SERVER['REQUEST_URI'] == '/spam' ) {
	echo("spam");
	exit;
}
