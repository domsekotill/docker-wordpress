#!/bin/bash
set -eux
shopt -s lastpipe

VERSION=${1-}


int_version()
{
	local IFS=. major minor patch
	read major minor patch <<<"$1"
	printf "%d%d%d" $((major*10000)) $((minor*100)) $patch
}

get_latest()
{
	declare -n array=$1
	local IFS=$'\n'
	sort -nr <<<"${!array[*]}" |
	head -n1
}

get_tarball()
{
	local release url version
	declare -A URLS=() RELEASES=()

	curl -sS https://api.github.com/repos/imagick/imagick/tags |
	jq -r '.[] | [.name, .tarball_url] | @tsv' |
	while read release url; do
		[[ $release =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] &&
			RELEASES[$(int_version $release)]=$release
		URLS[$release]=$url
	done

	if [[ -n $VERSION ]]; then
		url=${URLS[$VERSION]}
	else
		release=${RELEASES[`get_latest RELEASES`]}
		url=${URLS[$release]}
	fi

	curl -sSL $url | gunzip -c
}


cd $(mktemp -d)

CPPFLAGS=(
	-Dphp_strtolower=zend_str_tolower
)

get_tarball | tar -xf- --strip-components=1
phpize
./configure CPPFLAGS="${CPPFLAGS[*]}"
make install

echo "extension=imagick.so" > /usr/local/etc/php/conf.d/imagick.ini
