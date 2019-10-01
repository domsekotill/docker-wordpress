#!/bin/sh
set -eu

: ${BUILD_REPO?}
: ${DEPLOY_REPO?}

case ${CI_COMMIT_REF_NAME-develop} in
	master) tags="latest ${VERSION-}" ;;
	develop) tags="unstable" ;;
	*) exit 3 ;;
esac

set -x

docker pull ${BUILD_REPO}

for tag in $tags; do
	docker tag ${BUILD_REPO} ${DEPLOY_REPO}:${tag}
	docker push ${DEPLOY_REPO}:${tag}
done
