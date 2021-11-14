Feature: WP-CLI management tool

	Scenario Outline: Setting test commands
		When "<cmd>" is run
		Then nothing is seen from stderr

		Examples:
			| cmd                                                             |
			| wp option update timezone_string Europe/London                  |


	Scenario Outline: Getting test commands
		When "<cmd>" is run
		Then "<response>" is seen from stdout
		And nothing is seen from stderr

		Examples:
			| cmd                                       | response            |
			| wp option get timezone_string             | Europe/London       |


	Scenario Outline: Getting JSON test commands
		When "<cmd>" is run
		Then JSON is seen from stdout
		And nothing is seen from stderr

		Examples:
			| cmd                                                             |
			| wp option get timezone_string --format=json                     |
			| wp theme list --format=json                                     |
