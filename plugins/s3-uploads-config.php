<?php
/**
 * Plugin Name: S3-Uploads Configuration
 * Plugin URI: https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/tree/master/plugins
 * Description: Filters S3-Uploads parameters to configure the plugin
 * Licence: MPL-2.0
 * Licence URI: https://www.mozilla.org/en-US/MPL/2.0/
 * Author: Dominik Sekotill
 * Author URI: https://code.kodo.org.uk/dom
 */

add_filter( 's3_uploads_s3_client_params', function ( $params ) {
	$params['endpoint'] = S3_UPLOADS_ENDPOINT_URL;
	$params['bucket_endpoint'] = true;
	$params['disable_host_prefix_injection'] = true;
	$params['use_path_style_endpoint'] = true;
	$params['debug'] = WP_DEBUG && WP_DEBUG_DISPLAY;
	$params['region'] = '';
	return $params;
} );
