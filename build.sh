#!/bin/bash

get_latest() { :; }

get_version() {
	docker run --rm $1 nginx -V 2>&1 |
    sed -n '/nginx version:/s/.*nginx\///p'
}

build() {
	docker_build \
		${UPSTREAM_VERSION:+--build-arg nginx_version="${UPSTREAM_VERSION}"} \
		--tag $1
}
