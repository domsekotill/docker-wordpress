Feature: Return 404 for unknown path
	Regression check for "#14": don't redirect to the homepage when a 404 would
	be expected.

	Scenario Outline: Not found
		Given <path> does not exist
		When <path> is requested
		Then "Not Found" is returned

		Examples:
			| path              |
			| /this/is/missing  |
			| /this/is/missing/ |

	Scenario Outline: Bad pagination paths
		Given a page exists containing
		"""
		Some content
		"""
		When the page suffixed with <suffix> is requested
		Then <result> is returned

		Examples:
			| suffix | result    |
			| /      | OK        |
			| /0     | OK        |
			| /foo   | Not Found |
