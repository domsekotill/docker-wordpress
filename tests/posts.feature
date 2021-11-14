Feature: Posts
	Posts should be returned when their URL is requested.  The post index page
	should also be accessible.

	Background: A post exists
		Given a post exists containing
			"""
			This is some page content
			"""

	Scenario: Individual posts
		When the post is requested
		Then OK is returned
		And we will see the post text

	Scenario: Homepage post index
		When the homepage is requested
		Then OK is returned
		And we will see the post text

	Scenario: Non-homepage post index
		Given a blank page exists
		And is configured as the post index
		When the page is requested
		Then we will see the post text
