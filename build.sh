#!/bin/bash

get_latest() { :; }

get_version() {
	docker run --rm $1 wp core version
}

build() {
	# Get cached version of compile stage from registry if available
	docker_pull ${DOCKER_REPOSITORY}/compile:latest

	# Build compile stage cache, from last cached version if available
	docker_build \
		--target compile \
		--tag ${DOCKER_REPOSITORY}/compile:latest
	docker_push ${DOCKER_REPOSITORY}/compile:latest

	docker_build \
		${UPSTREAM_VERSION:+--build-arg wp_version="${UPSTREAM_VERSION}"} \
		--tag $1

		# --build-arg base_image="${WORDPRESS_BASE_IMAGE:-php:7.3-fpm}" \
}
