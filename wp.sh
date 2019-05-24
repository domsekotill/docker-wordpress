#!/bin/sh
# Lets not beat about the bush, preventing the tool which installs WP from 
# installing it as root is idiocy. WP needs to be installed owned by a user 
# seperate from the server's user. 'root' is available for such, besides which 
# root in a container is not really root.
exec php /usr/local/lib/wp-cli.phar --allow-root "$@"
