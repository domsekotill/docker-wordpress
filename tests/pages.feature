Feature: Pages
	Pages should be returned when their URL is requested.

	Background: A page exists
		Given a page exists containing
			"""
			This is some page content
			"""

	Scenario: A page type post
		When the page is requested
		Then OK is returned
		And we will see the page text

	Scenario: Static homepage
		Given the page is configured as the homepage
		When the homepage is requested
		Then OK is returned
		And we will see the page text
