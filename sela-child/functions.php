<?php

/* Style loading boilerplate */
add_action( 'wp_enqueue_scripts', 'sela_child_enqueue_styles' );

function sela_child_enqueue_styles()
{
	wp_enqueue_style( 'sela-style',
		get_template_directory_uri() . '/style.css'
	);

	wp_enqueue_style( 'sela-child-style',
		get_stylesheet_directory_uri() . '/style.css',
		array( 'sela-style' ),
		wp_get_theme()->get('Version')
	);

//	wp_enqueue_style( 'sela-child-bootstrap',
//		get_stylesheet_directory_uri() . '/bootstrap3/css/bootstrap.min.css',
//		array( 'sela-style' ),
//		wp_get_theme()->get('Version')
// 	);
}
