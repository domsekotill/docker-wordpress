<?php
/**
 * Plugin Name: S3-Uploads
 * Plugin URI: https://github.com/humanmade/S3-Uploads
 * Description: S3-Uploads with custom endpoint configuration
 * Licence: GPL-2.0+
 * Licence URI: https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
 * Author: Human Made Limited
 * Author URI: http://hmn.md/
 **/

if ( defined( 'S3_UPLOADS_ENDPOINT_URL' ) || defined( 'WP_CLI' ) ):

add_filter( 's3_uploads_s3_client_params', function ( $params ) {
	$params['endpoint'] = S3_UPLOADS_ENDPOINT_URL;
	$params['bucket_endpoint'] = true;
	$params['disable_host_prefix_injection'] = true;
	$params['use_path_style_endpoint'] = true;
	$params['debug'] = WP_DEBUG && WP_DEBUG_DISPLAY;
	$params['region'] = '';
	return $params;
} );

require WPMU_PLUGIN_DIR . '/s3-uploads/s3-uploads.php';

endif;
