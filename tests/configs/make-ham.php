// <?php

// Serves the word "ham" at /ham
// Used for checking that this file has been loaded correctly

if ( !defined('WP_CLI') && $_SERVER['REQUEST_URI'] == '/ham' ) {
	echo("ham");
	exit;
}
