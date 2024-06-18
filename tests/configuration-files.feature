@long-running

Feature: Configuration files and environment
	Test that all mounted configurations are picked up as expected, and
	configurations have their intended effect.

	Background:
		Given the site is not running

	Scenario: Nested directories of "*.conf" files are found and read
		Given /etc/wordpress/sela-theme.conf contains:
			"""
			THEMES=(sela)
			"""
		And plugins.conf is mounted in /etc/wordpress/extras/
		When the site is started
		Then the theme sela is active
		And the plugin wp-dummy-content-generator is installed

	Scenario: Nested directories of "*config.php" files are found and integrated
		Given make-spam.php is mounted in /etc/wordpress/ as spam-config.php
		And make-ham.php is mounted in /etc/wordpress/ as ham-config.php
		And make-eggs.php is mounted in /etc/wordpress/extras/ as config.php
		When the site is started
		And /spam is requested
		Then OK is returned
		And the response body contains:
			"""
			spam
			"""
		When /ham is requested
		Then OK is returned
		And the response body contains:
			"""
			ham
			"""
		When /eggs is requested
		Then OK is returned
		And the response body contains:
			"""
			eggs
			"""

	Scenario: Check that WP_CONFIGS expands wildcards from passed-in values
		Given make-ham.php is mounted in /tmp
		And make-eggs.php is mounted in /tmp
		And the environment variable WP_CONFIGS is "/tmp/*.php"
		When /ham is requested
		Then OK is returned
		And the response body contains:
			"""
			ham
			"""
		When /eggs is requested
		Then OK is returned
		And the response body contains:
			"""
			eggs
			"""

	Scenario: A "plugins.txt" file is used as a source of plugins
		Given plugins.txt is mounted in /etc/wordpress/
		When the site is started
		Then the plugin wp-dummy-content-generator is installed

	Scenario: A "themes.txt" file is used as a source of plugins
		Given /etc/wordpress/themes.txt contains:
			"""
			sela
			"""
		When the site is started
		Then the theme sela is active

	Scenario: A "languages.txt" file is used as a source of language packs
		Given /etc/wordpress/languages.txt contains:
			"""
			de_DE
			"""
		When the site is started
		And /wp-login.php is requested
		Then the response body contains:
			"""
			value="de_DE"
			"""

	Scenario: When PLUGINS_LIST is provided, it replaces "plugins.txt"
		Given bad-plugins.txt is mounted in /etc/wordpress/ as plugins.txt
		And plugins.txt is mounted in /etc/wordpress/ as real-plugins.txt
		And the environment variable PLUGINS_LIST is "/etc/wordpress/real-plugins.txt"
		When the site is started
		Then the plugin wp-dummy-content-generator is installed

	Scenario: When THEMES_LIST is provided, it replaces "themes.txt"
		Given /etc/wordpress/themes.txt contains:
			"""
			twentytwentythree
			"""
		And /etc/wordpress/sela-theme.txt contains:
			"""
			sela
			"""
		And the environment variable THEMES_LIST is "/etc/wordpress/sela-theme.txt"
		When the site is started
		Then the theme sela is active

	Scenario: When LANGUAGES_LIST is provided, it replaces "langages.txt"
		Given /etc/wordpress/languages.txt contains:
			"""
			de_DE
			"""
		And /etc/wordpress/french.txt contains:
			"""
			fr_FR
			"""
		And the environment variable LANGUAGES_LIST is "/etc/wordpress/french.txt"
		When the site is started
		And /wp-login.php is requested
		Then the response body contains:
			"""
			value="fr_FR"
			"""
