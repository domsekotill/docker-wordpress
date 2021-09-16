<?php
/**
 * Copyright 2019-2021 Dominik Sekotill <dom.sekotill@kodo.org.uk>
 *
 * Plugin Name: Docker Image Integration
 * Plugin URI: https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/tree/master/plugins
 * Description: Hooks in behaviour for operating cleanly in a Docker environment
 * Licence: MPL-2.0
 * Licence URI: https://www.mozilla.org/en-US/MPL/2.0/
 * Author: Dominik Sekotill
 * Author URI: https://code.kodo.org.uk/dom
 */


// Media URL Fix

add_action( 'plugins_loaded', function() {
	add_filter( 'upload_dir', function( $paths ) {
		$baseurl = parse_url( $paths['baseurl'] );
		$fullurl = parse_url( $paths['url'] );
		$subdir = $paths['subdir'];

		$baseurl['path'] = '/media';
		$fullurl['path'] = '/media' . ($subdir ? "/{$subdir}" : '');

		$paths['baseurl'] = unparse_url( $baseurl );
		$paths['url']     = unparse_url( $fullurl );

		return $paths;
	});
});


// Block File Modification

add_filter(
	'file_mod_allowed',

	function( $setting, $context ) {
		if ( $context == 'automatic_updater' ) {
			return true;
		}
		return $setting;
	},

	10, 2
);


// Disable Plugins & Themes

add_filter(
	'user_has_cap',

	function( $allcaps, $caps, $args ) {
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
	},

	10, 3
);


// S3-Uploads Integration

if ( defined( 'S3_UPLOADS_ENDPOINT_URL' ) || defined( 'WP_CLI' ) ):

add_filter(
	's3_uploads_s3_client_params',

	function ( $params ) {
		$params['endpoint'] = S3_UPLOADS_ENDPOINT_URL;
		$params['bucket_endpoint'] = true;
		$params['disable_host_prefix_injection'] = true;
		$params['use_path_style_endpoint'] = true;
		$params['debug'] = WP_DEBUG && WP_DEBUG_DISPLAY;
		$params['region'] = '';
		return $params;
	}
);

endif;


// Functions

function unparse_url( array $parts ) {
	return (
		(isset($parts['scheme'])   ?  "{$parts['scheme']}://" : '') .
		(isset($parts['user'])     ?    $parts['user']        : '') .
		(isset($parts['pass'])     ? ":{$parts['pass']}"      : '') .
		(isset($parts['user']) || isset($parts['pass']) ? '@' : '') .
		(isset($parts['host'])     ?    $parts['host']        : '') .
		(isset($parts['port'])     ? ":{$parts['port']}"      : '') .
		(isset($parts['path'])     ?    $parts['path']        : '') .
		(isset($parts['query'])    ? "?{$parts['query']}"     : '') .
		(isset($parts['fragment']) ? "#{$parts['fragment']}"  : '')
	);
}
