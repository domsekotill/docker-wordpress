Feature: Script Access and Restrictions
	The user-facing parts of a WordPress application should all be either static
	resources or channeled through the root *index.php* entrypoint.  However PHP
	is architectured in such a way that, if left unrestricted, any PHP file
	could be accessed as a script.

	In many cases protections have been put in place in WordPress' PHP files to
	prevent circumvention of access restriction, as well as some plugins.
	However this should never be relied on as it introduces additional
	complexity and may not have been thoroughly tested.  It could also be
	considered a UI bug if a non-404 code is returned.

	To confuse matters the administration interface *is* accessed in a
	one-script-per-endpoint manner.

	Scenario Outline: Direct file access
		When <path> is requested
		Then <result> is returned

		Examples: Static files
			| path                                                | result    |
			| /wp-includes/images/w-logo-blue.png                 | OK        |
			| /wp-admin/images/w-logo-blue.png                    | OK        |
			| /readme.html                                        | Not Found |
			| /composer.json                                      | Not Found |
			| /composer.lock                                      | Not Found |

		Examples: Non-entrypoint PHP files
			| path                                                | result    |
			| /wp-activate.php                                    | Not Found |
			| /wp-blog-header.php                                 | Not Found |
			| /wp-comments-post.php                               | Not Found |
			| /wp-config.php                                      | Not Found |
			| /wp-cron.php                                        | Not Found |
			| /wp-load.php                                        | Not Found |
			| /wp-mail.php                                        | Not Found |
			| /wp-settings.php                                    | Not Found |
			| /wp-signup.php                                      | Not Found |
			| /wp-trackback.php                                   | Not Found |
			| /xmlrpc.php                                         | Not Found |
			| /wp-includes/user.php                               | Not Found |

		Examples: Entrypoint PHP files
			| path                                                | result    |
			| /                                                   | OK        |
			| /index.php                                          | 301       |
			| /wp-login.php                                       | OK        |
			| /wp-admin/                                          | 302       |
			| /wp-admin/index.php                                 | 302       |

	Scenario: Check the JSON API is accessible
		When /wp-json/wp/v2/ is requested
		Then OK is returned
		And the response body is JSON
