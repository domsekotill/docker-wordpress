#!/bin/sh
# Copyright 2019-2021 Dominik Sekotill <dom.sekotill@kodo.org.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Lets not beat about the bush, preventing the tool which installs WP from
# installing it as root is idiocy. WP needs to be installed owned by a user
# seperate from the server's user. 'root' is available for such, besides which
# root in a container is not really root.
exec php -d memory_limit=512M /usr/local/lib/wp-cli.phar --allow-root "$@"
