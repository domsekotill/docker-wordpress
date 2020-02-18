# syntax = docker/dockerfile:1.0-experimental

ARG nginx_version=latest
FROM nginx:${nginx_version} as nginx
LABEL uk.org.kodo.maintainer = "Dom Sekotill <dom.sekotill@kodo.org.uk>"
COPY nginx.conf /etc/nginx/conf.d/default.conf


FROM php:7.3-fpm-alpine as deps
RUN --mount=type=bind,source=scripts/install-deps.sh,target=/stage /stage

FROM deps as compile
RUN --mount=type=bind,source=scripts/compile.sh,target=/stage /stage

FROM deps

LABEL uk.org.kodo.maintainer "Dom Sekotill <dom.sekotill@kodo.org.uk>"

ARG wp_version=latest
WORKDIR /app
ENV WORDPRESS_ROOT=/app

COPY wp.sh /usr/local/bin/wp
COPY --from=compile /usr/local/etc/php /usr/local/etc/php
COPY --from=compile /usr/local/lib/php /usr/local/lib/php
RUN --mount=type=bind,source=scripts/install-wp.sh,target=/stage \
    /stage ${wp_version}

COPY probe.php wp-content/mu-plugins/
COPY fpm.conf /usr/local/etc/php-fpm.d/image.conf
COPY opcache.ini /usr/local/etc/php/conf.d/opcache-recommended.ini
COPY wp-config.php /usr/share/wordpress/wp-config.php
COPY entrypoint.sh /bin/entrypoint

# PAGER is used by the wp-cli tool, the default 'less' is not installed
ENV PAGER=more

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
