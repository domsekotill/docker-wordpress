#!/bin/bash

get_latest() {
	wget -O- 'http://api.wordpress.org/core/version-check/1.7/' |
		sed -r 's/^.*"current":"([^"]+)".*$/\1/'
}

get_version() {
	echo "${UPSTREAM_VERSION}"
}

build() {
	docker_build \
		--build-arg wp_version="${UPSTREAM_VERSION}" \
		--tag $1

		# --build-arg base_image="${WORDPRESS_BASE_IMAGE:-php:7.3-fpm}" \
}
