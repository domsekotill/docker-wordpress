<?php
/**
 * The template used for displaying page content.
 *
 * @package Sela
 */


$title = the_title(null, null, false);

if ( function_exists('get_nskw_subtitle') ) {
	$subtitle = get_nskw_subtitle();
} else {
	$subtitle = '';
}

if ( $subtitle == '' ) {
	$title_class = 'entry-title';
} else {
	$title_class = 'entry-title has-subtitle';
}

?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

	<header class="entry-header">
		<h1 class="<?php print($title_class); ?>"><?php print($title); ?></h1>
		<?php if ( $subtitle != '' ): ?>
			<h5 class="entry-subtitle"><?php print($subtitle); ?></h5>
		<?php endif; ?>
	</header><!-- .entry-header -->

	<div class="entry-content">
		<?php the_content(); ?>
		<?php
			wp_link_pages( array(
				'before' => '<div class="page-links">' . __( 'Pages:', 'sela' ),
				'after'  => '</div>',
			) );
		?>

	</div><!-- .entry-content -->
	<?php edit_post_link( __( 'Edit', 'sela' ), '<footer class="entry-meta"><span class="edit-link">', '</span></footer>' ); ?>

</article><!-- #post-## -->
