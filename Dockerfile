# syntax = docker/dockerfile:1.0-experimental

ARG nginx_version=latest
FROM nginx:${nginx_version} as nginx
LABEL uk.org.kodo.maintainer = "Dom Sekotill <dom.sekotill@kodo.org.uk>"
COPY data/nginx /etc/nginx


ARG php_version=
FROM php:${php_version:+$php_version-}fpm-alpine as deps
RUN --mount=type=bind,source=scripts/install-deps.sh,target=/stage /stage

FROM deps as compile
RUN --mount=type=bind,source=scripts/compile.sh,target=/stage /stage

FROM deps as fastcgi

LABEL uk.org.kodo.maintainer "Dom Sekotill <dom.sekotill@kodo.org.uk>"

ARG wp_version=latest
WORKDIR /app
ENV WORDPRESS_ROOT=/app

COPY --from=compile /usr/local/etc/php /usr/local/etc/php
COPY --from=compile /usr/local/lib/php /usr/local/lib/php
COPY scripts/wp.sh /usr/local/bin/wp
COPY data/composer.json /app/composer.json
RUN --mount=type=bind,source=scripts/install-wp.sh,target=/stage \
    /stage ${wp_version}

COPY plugins/* wp-content/mu-plugins/
COPY data/fpm.conf /usr/local/etc/php-fpm.d/image.conf
COPY data/opcache.ini /usr/local/etc/php/conf.d/opcache-recommended.ini
COPY data/wp-config.php /usr/share/wordpress/wp-config.php
COPY scripts/entrypoint.sh /bin/entrypoint

# PAGER is used by the wp-cli tool, the default 'less' is not installed
ENV PAGER=more

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
