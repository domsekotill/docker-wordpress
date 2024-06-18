<?php
/*
Plugin Name: Test Plugin
Description: Assists in the testing of some scenarios
*/

add_action( 'rest_api_init', function() {
	register_rest_route( 'test/v1', '/write-cache', array(
		'methods' => WP_REST_Server::READABLE,
		'callback' => function($request) {
			if ( !isset($request['file']) ) {
				return new WP_Error('Missing param file');
			}
			$file = WP_CONTENT_DIR . "/cache/{$request['file']}";
			file_put_contents($file, "Generated file");
			return rest_ensure_response( "Cache file created" );
		},
		'args' => array(
			'file' => array(
				'description' => 'File to touch on the server host',
				'type' => 'string',
			)
		)
	));
});

/* register_activation_hook( __FILE__, function() { */
/* 	if ( !defined('WP_CLI') && $_SERVER['REQUEST_URI'] == '/test-cache' ) { */
/* 		$file = WP_CONTENT_DIR . "/cache/${_GET['file']}"; */
/* 		file_put_contents($file, "Generated file"); */
/* 		wp_die("Cache file created", 200); */
/* 	} */
/* }); */
