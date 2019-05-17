<?php
/**
 * Template Name: Front Page
 *
 * @package Sela-Child
 */

get_header(); ?>

	<div id="primary" class="content-area front-page-content-area">
		<?php while ( have_posts() ) : the_post(); ?>
			<div class="hero">

				<?php if ( has_post_thumbnail() ) : ?>
				<figure class="hero-content">
					<?php the_post_thumbnail( 'sela-hero-thumbnail' ); ?>
					<div class="hero-content-overlayer">
						<div class="hero-container-outer">
							<div class="hero-container-inner">
								<?php get_template_part( 'content', 'page' ); ?>
							</div><!-- .hero-container-inner -->
						</div><!-- .hero-container-outer -->
					</div><!-- .hero-content-overlayer -->
				</figure><!-- .hero-content -->

				<?php else : ?>
					<?php get_template_part( 'content', 'page' ); ?>
				<?php endif; ?>

			</div><!-- .hero -->
		<?php endwhile; ?>
	</div><!-- #primary -->

	<?php get_sidebar( 'front-page' ); ?>

	<?php
		$testimonials = new WP_Query( array(
			'post_type'      => 'jetpack-testimonial',
			'order'          => 'ASC',
			'orderby'        => 'menu_order',
			'posts_per_page' => 2,
			'no_found_rows'  => true,
		) );
	?>

	<?php if ( $testimonials->have_posts() ) : ?>
	<div id="front-page-testimonials" class="front-testimonials testimonials">
		<div class="grid-row">
		<?php
			while ( $testimonials->have_posts() ) : $testimonials->the_post();
				 get_template_part( 'content', 'testimonial' );
			endwhile;
			wp_reset_postdata();
		?>
		</div>
	</div><!-- .testimonials -->
	<?php endif; ?>

<?php get_sidebar( 'footer' ); ?>
<?php get_footer(); ?>
