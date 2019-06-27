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
  the files are specifically written to honour the environment variables.

- For array options the value provided in the environment variable will 
  become the first item (index 0).


Convenience Files
-----------------

In addition to the values specified in `*.conf` files, for convenience the 
files specified by [**PLUGINS_LIST**](#plugins_list), 
[**THEMES_LIST**](#themes_list) and [**LANGUAGES_LIST**](#languages_list) 
options are optional plain text files listing additional entries (one per 
line) to append to the [**PLUGINS**](#plugins), [**THEMES**](#themes) and 
[**LANGUAGES**](#languages) option arrays respectively.


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

The path to a file containing lines to append to 
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

The path to a file containing lines to append to [**PLUGINS**](#plugins).

### PHP_DIRECTIVES

**Type**: array\
**Required**: no\
**Default**: "upload_max_filesize=20M", "post_max_size=20M"

An array of "key=value" strings declaring [PHP directives][].

**Note:** These values may alternatively be supplied as container command 
arguments prefixed with the '-d' flag:
`-d upload_max_filesize=20M -d post_max_size=20M`

### STATIC_PATTERNS

**Type**: array\
**Required**: no\
**Default**: various documentation files and formats, certificates and i18n 
data files

This is an array of shell wildcard patterns (non-GNU extensions) matching 
files which will NOT be copied to the static files directory.

**Note:** Files with a .php extension are never copied to the static files 
directory.

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

The path to a file containing lines to append to [**THEMES**](#themes).

### WP_CONFIG_EXTRA

**Type**: string\
**Required**: no\
**Default**: /etc/wordpress/wp-config-extra.php

This is the path to a file containing additional content for *wp-config.php* 
to go near the end of the file.

### WP_CONFIG_LINES

**Type**: array\
**Required**: no

This is an array of lines (without terminating carriage-returns) to add to 
*wp-config.php* just before the contents of the file in 
[**WP_CONFIG_EXTRA**](#wp_config_extra).


[php directives]:
  https://www.php.net/manual/en/ini.list.php
  "PHP: List of php.ini directives"
