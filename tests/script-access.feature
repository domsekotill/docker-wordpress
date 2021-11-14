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
			| /wp-comments-post.php                               | 405       |

	Scenario: Check the JSON API is accessible
		When /wp-json/wp/v2/ is requested
		Then OK is returned
		And the response body is JSON

	Scenario: "GET /wp-comments-post.php" is not allowed
		When /wp-comments-post.php is requested
		Then 405 is returned
		And the "Allow" header's value is "POST"

	Scenario: "POST /wp-contents-post.php" accepts content
		Given a blank post exists
		When data is sent with POST to /wp-comments-post.php
		"""
		comment_post_id={context.post[ID]}&author=John+Smith&email=j.smith@example.com&comment=First+%F0%9F%8D%86
		"""
		Then OK is returned
		# (Why 200 instead of 201? Probably the same reason 200 is returned when
		# there are missing values?! It's WordPress.)
