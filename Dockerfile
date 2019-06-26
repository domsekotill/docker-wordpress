# syntax = docker/dockerfile:1.0-experimental

ARG nginx_version=latest
FROM nginx:${nginx_version} as nginx
LABEL uk.org.kodo.maintainer = "Dom Sekotill <dom.sekotill@kodo.org.uk>"
COPY nginx.conf /etc/nginx/conf.d/default.conf


FROM php:7.3-fpm-alpine as deps
RUN --mount=type=bind,source=scripts,target=/scripts /scripts/install-deps.sh

FROM deps as compile
RUN --mount=type=bind,source=scripts,target=/scripts /scripts/compile.sh

FROM deps

LABEL uk.org.kodo.maintainer "Dom Sekotill <dom.sekotill@kodo.org.uk>"

ARG wp_version=latest
WORKDIR /app
VOLUME /app/wp-content
ENV WORDPRESS_ROOT=/app

ADD https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    /usr/local/lib/wp-cli.phar
COPY wp.sh /usr/local/bin/wp
COPY --from=compile /usr/local/etc/php /usr/local/etc/php
COPY --from=compile /usr/local/lib/php /usr/local/lib/php
RUN --mount=type=bind,source=scripts,target=/scripts \
    /scripts/install-wp.sh ${wp_version}

COPY opcache.ini /usr/local/etc/php/conf.d/opcache-recommended.ini
COPY entrypoint.sh /bin/entrypoint

# PAGER is used by the wp-cli tool, the default 'less' is not installed
ENV PAGER=more

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
