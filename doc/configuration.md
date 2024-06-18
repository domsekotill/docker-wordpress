Configuration
=============

Configuration files are mounted (or added in a child image) under 
*/etc/wordpress*.  All files in this directory or any subdirectory which 
match `*.conf` will be sourced as Bash scripts. The valid variable names 
which are understood by the entrypoint script are listed below.

Any Bash commands are valid in the `*.conf` files, allowing the 
configuration process to be flexible.

It is recommended that when setting the array variables the "+=" operator be 
used to append, rather than replace values.  This allows separate config 
files to cooperatively configure the service.  It also appends to the 
default values, if any.

The order of file sourcing is Bash's wildcard matching; numeric then 
alphabetic for both files and directories together, and descending into 
directories as they are found. The following shows some example files in 
their sourced order:

```shell
$ ls -1f **/*.conf
00-init.conf
01-first-dir/initial.conf
01-first-dir/next.conf
01-first-dir/zz-final.conf
another.conf
second-dir/example.conf
zz-final.conf
```


Environment Variables
---------------------

Any of the configuration values may also be passed as environment variables 
to the container, however:

- Unlike the way most configuration systems treat environment variables, 
  they do not overwrite options provided in the configuration files unless 
  the files are specifically written to honour the environment variables, 
  for instance by using the "+=" operator to append to arrays.

- For array options the value provided will be split on whitespace. 
  Unfortunately at the moment there is no way to escape or quote whitespace 
  within items.  If you find yourself needing to add items with whitespace, 
  consider using configuration files instead, which are interpreted with 
  Bash, or one of the [convenience files](#convenience-files).


Convenience Files
-----------------

In addition to the values specified in `*.conf` files, for convenience the 
files specified by [**PLUGINS_LIST**](#plugins_list), 
[**THEMES_LIST**](#themes_list) and [**LANGUAGES_LIST**](#languages_list) 
options are optional plain text files listing additional entries (one per 
line) to append to the [**PLUGINS**](#plugins), [**THEMES**](#themes) and 
[**LANGUAGES**](#languages) option arrays respectively.

> **Note:** Every line in these files MUST be correctly terminated in the Unix 
> style (with a line-feed character). Please pay special attention to the final 
> line as some text editors do not correctly terminate them.


Options
-------

### DB_NAME

**Type**: string\
**Required**: yes

The name of the MySQL database.

### DB_USER

**Type**: string\
**Required**: yes

The username if credential authentication is required to access the 
database.

### DB_PASS

**Type**: string\
**Required**: no

The password if credential authentication is required to access the 
database.

### DB_HOST

**Type**: string\
**Required**: no\
**Default**: localhost

The hostname of the MySQL server providing the database.

### DEBUG

**Type**: string\
**Format**: comma or space separated list\
**Required**: no\
**Example**: "display,script"

If set (even if empty, unless it contains the value `false`) the Wordpress option 
[`WP_DEBUG`][wp_debug] is enabled which will cause error, warning and notice messages to be 
printed to the container output.

The value can contain any of the following, separated by commas or spaces (other values will 
cause an error):

| Value                           | Effect                                                 |
| -----                           | ------                                                 |
| `true` \| `yes` \| `y` \| `on`  | Default if `DEBUG` is set                              |
| `false` \| `no` \| `n` \| `off` | Disables default behaviour, can be combined with others|
| `all`                           | Shorthand for `"display,script,s3"`                    |
| `display`                       | Enables displaying messages in output (not recommended)|
| `script`                        | Enables [`SCRIPT_DEBUG`][script_debug]                 |
| `s3`                            | Enables debug on S3 transfers (may cause memory issues)|

> **Note:**  `false` can be combined with `script` or `s3` to enable the latter features 
> without [`WP_DEBUG`][wp_debug].

[wp_debug]:
  https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/#wp_debug

[script_debug]:
  https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/#script_debug

### HOME_URL

**Type**: string\
**Required**: no\
**Default**: [**SITE_URL**](#site_url) with path components removed

The URL where visitors should first be directed to when accessing the web site. It defaults 
to the root path of [**SITE_URL**](#site_url).

### LANGUAGES

**Type**: array\
**Required**: no

This is an array of language packs to install at startup.  Items are POSIX 
locale language tags. (e.g. 'en_US').  If a locale is not available for 
Wordpress core the startup will fail.  If it is not available for a plugin 
the missing language pack will be silently ignored.

### LANGUAGES_LIST

**Type**: string\
**Required**: no\
**Default**: /etc/wordpress/languages.txt

The path to a plain text file containing lines to append to 
[**LANGUAGES**](#languages).

### PLUGINS

**Type**: array\
**Required**: no

This is an array of plugins to install at startup.  Items can be plugin 
names or URLs to .zip files.  When given a name the version installed will 
be the latest stable available in the wordpress.org registry.

### PLUGINS_LIST

**Type**: string\
**Required**: no\
**Default**: /etc/wordpress/plugins.txt

The path to a plain text file containing lines to append to 
[**PLUGINS**](#plugins).

### PHP_DIRECTIVES

**Type**: array\
**Required**: no\
**Default**: "upload_max_filesize=20M", "post_max_size=20M"

An array of "key=value" strings declaring [PHP directives][].

> **Note:** These values may alternatively be supplied as container command 
> arguments preceded by the '-d' flag:
> `-d upload_max_filesize=20M -d post_max_size=20M`

### S3_MEDIA_ENDPOINT

**Type**: string\
**Required**: if using S3 for uploaded media\
**Format**: URL\
**Example**: "https://s3.example.com/bucket/path"

A URL to an S3 or S3-like API, including any region and bucket names, and any path in the 
bucket to append.

### S3_MEDIA_KEY

**Type**: string\
**Required**: if using S3 for uploaded media

An access key allowing write access to the S3 endpoint given by 
[**S3_MEDIA_ENDPOINT**](#s3_media_endpoint).

### S3_MEDIA_SECRET

**Type**: string\
**Required**: if using S3 for uploaded media

The secret paired with the access key given in [**S3_MEDIA_KEY**](#s3_media_key).

### S3_MEDIA_REWRITE_URL

**Type**: string\
**Required**: no\
**Format**: URL\
**Example**: "https://my.domain.example.org/"

A base URL for viewers to access uploaded media.  This allows caching proxies, such as CDNs, 
to be used for accessing files.

### SANDBOX_MODE

**Type**: flag\
**Required**: no

If set, [sandbox mode](sandbox-mode.md) is enabled.

**Do not set on production sites**

### SITE_ADMIN

**Type**: string\
**Required**: no\
**Default**: "admin"

A user name for the initial administrator account.

> **Note:** This is only used for first-run setup; it can be changed from the admin 
> interface.

### SITE_ADMIN_EMAIL

**Type**: string\
**Required**: no\
**Default**: "admin@{DOMAIN}" where *DOMAIN* is extracted from [**SITE_URL**](#site_url)

An email address for the new administrator account (see [**SITE_ADMIN**](#site_admin)).

> **Note:** This is only used for first-run setup; it can be changed from the admin 
> interface.

### SITE_ADMIN_PASSWORD

**Type**: string\
**Required**: no

A password for the new administrator account (see [**SITE_ADMIN**](#site_admin)).
If left unset a random password will be generated and reported in stderr logging; after 
sign-in the user SHOULD then create a new password through the user management interface.

> **Note:** This is only used for first-run setup; it can be changed from the admin 
> interface.

### SITE_TITLE

**Type**: string\
**Required**: no\
**Default**: "New Wordpress Site"

A title for the web site, displayed in various strategic locations.

> **Note:** This is only used for first-run setup; it can be changed from the admin 
> interface.

### SITE_URL

**Type**: string\
**Required**: yes\
**Example**: "https://my.example.org/blog"

The base URL where the Wordpress app is hosted externally.  This MUST include at least 
a protocol scheme (e.g. "https://") and a host name; it MAY contain a port, when external 
access is via a non-standard port; if MAY contain a path component, when the Wordpress app 
is not accessed at the root path.

### STATIC_PATTERNS

**Type**: array\
**Required**: no\
**Default**: various documentation files and formats, certificates and i18n 
data files

This is an array of shell wildcard patterns (non-GNU extensions) matching 
files which will NOT be copied to the static files directory.

> **Note:** Files with a .php extension are never copied to the static files 
> directory.

### THEMES

**Type**: array\
**Required**: no

This is an array of themes to install at startup.  Items can be theme names 
or URLs to .zip files.  When given a name the version installed will be the 
latest stable available in the wordpress.org registry.

### THEMES_LIST

**Type**: string\
**Required**: no\
**Default**: /etc/wordpress/themes.txt

The path to a plain text file containing lines to append to 
[**THEMES**](#themes).

### WP_CONFIGS

**Type**: array\
**Required**: no\
**Default**: /etc/wordpress/**/*config.php

This is an array of files to include in wp-config.php.  The default includes 
a wildcard which is expanded.  Wildcards in the environment variable will 
also be expanded.


[php directives]:
  https://www.php.net/manual/en/ini.list.php
  "PHP: List of php.ini directives"
