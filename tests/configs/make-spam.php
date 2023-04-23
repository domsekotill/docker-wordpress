// <?php

// Serves the word "spam" at /spam
// Used for checking that this file has been loaded correctly

if ($_SERVER['REQUEST_URI'] == '/spam') {
	echo("spam");
	exit;
}
