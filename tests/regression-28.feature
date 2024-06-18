@wip
Feature: Page cache directory
	Ensure that the page cache directory at WP_CONTENT_DIR/cache is writable for
	plugins, but is not served by the server.

	Scenario: After the entrypoint has completed, there is a writable cache dir
		Given the site is not running
		And test-cache.php is mounted in /app/wp-content/mu-plugins/
		When the site is started
		And /wp-json/test/v1/write-cache?file=foo.txt is requested
		Then OK is returned
		And /app/wp-content/cache/foo.txt exists in the backend

	Scenario: The contents of the cache dir are not served by the proxy
		Given /app/wp-content/cache/foo exists in the backend
		When /wp-content/cache/foo is requested
		Then Not Found is returned
