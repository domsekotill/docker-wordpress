@long-running

Feature: Site configuration variables
	Test that setting SITE_* variables has the expected effect.

	Scenario: Check default admin user's details and site name
		When / is requested
		Then the response body contains:
		"""
		Wordpress Site
		"""
		And the email address of admin is "admin@test.example.com"
		And the password of admin is not "password1"

	Scenario: Set variables and check again
		Given the site is not running
		And the environment variable SITE_TITLE is "Awesome Website of King Arthur"
		And the environment variable SITE_ADMIN is "arthur"
		And the environment variable SITE_ADMIN_EMAIL is "the.king@kodo.org.uk"
		And the environment variable SITE_ADMIN_PASSWORD is "password1"

		When the site is started
		And / is requested
		Then OK is returned
		And the response body contains:
		"""
		<title>Awesome Website of King Arthur</title>
		"""
		And the email address of arthur is "the.king@kodo.org.uk"
		And the password of arthur is "password1"
