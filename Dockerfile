# syntax = docker/dockerfile:1.0-experimental

ARG nginx_version=latest
FROM nginx:${nginx_version} as nginx
LABEL uk.org.kodo.maintainer = "Dom Sekotill <dom.sekotill@kodo.org.uk>"
COPY nginx.conf /etc/nginx/conf.d/default.conf


FROM php:7.3-fpm as deps
RUN apt-get update \
 && apt-get install -y \
	libgmp10 \
	libjpeg62 \
	libpng16-16 \
    libzip4 \
 &&:


FROM deps as compile
RUN apt-get update \
 && apt-get install -y \
	libgmp-dev \
	libjpeg-dev \
	libpng-dev \
    libzip-dev \
 && docker-php-ext-configure gd --with-png-dir=/usr --with-jpeg-dir=/usr \
 && docker-php-ext-install gd mysqli opcache gmp zip \
 &&:


FROM deps

LABEL uk.org.kodo.maintainer "Dom Sekotill <dom.sekotill@kodo.org.uk>"

COPY --from=compile /usr/local/etc/php /usr/local/etc/php
COPY --from=compile /usr/local/lib/php /usr/local/lib/php
COPY wp.sh /usr/local/bin/wp
ADD https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar /usr/local/bin/wp.php

WORKDIR /app
VOLUME /app/wp-content
ENV WORDPRESS_ROOT=/app

ARG wp_version=latest
RUN wp core download --skip-content --locale=en_GB --version=${wp_version}

COPY opcache.ini /usr/local/etc/php/conf.d/opcache-recommended.ini
COPY entrypoint.sh /bin/entrypoint

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
