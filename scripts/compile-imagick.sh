#!/bin/bash
set -eux

cd $(mktemp -d)

git clone --depth 1 https://github.com/imagick/imagick.git .
phpize
./configure
make install

echo "extension=imagick.so" > /usr/local/etc/php/conf.d/imagick.ini
