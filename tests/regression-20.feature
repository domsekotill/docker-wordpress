Feature: Return favicons when requests
	Regression check for "#20": Fix/remove favicon.ico intercept in Nginx

	An icon should always be served when requesting "/favicon.ico", either one
	added by the owner, or a default icon.

	Scenario: Default icon
		When /favicon.ico is requested
		Then 302 is returned
		And the "Location" header's value is "http://test.example.com/wp-includes/images/w-logo-blue-white-bg.png"

	Scenario: Owner supplied icon
		Given /app/static/wp/favicon.ico exists in the frontend
		When /favicon.ico is requested
		Then 200 is returned
