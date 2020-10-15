<?php
/**
 * Plugin Name: Media URL Fix
 * Plugin URI: https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/tree/master/plugins
 * Description: Adjusts the media URL path base to /media, where the Nginx instance is hosting it.
 * Licence: MPL-2.0
 * Licence URI: https://www.mozilla.org/en-US/MPL/2.0/
 * Author: Dominik Sekotill
 * Author URI: https://code.kodo.org.uk/dom
 */

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
