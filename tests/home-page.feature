Feature: Homepage
	The homepage should display either a static page or a feed

	Scenario: static homepage
		Given a page exists containing
			"""
			This is some page content
			"""
		And the page is configured as the homepage
		When the homepage is requested
		Then OK is returned
		And we will see the page text

	Scenario: feed homepage
		Given a post exists containing
			"""
			This is some post content
			"""
		And the homepage is the default
		When the homepage is requested
		Then OK is returned
		And we will see the post text
