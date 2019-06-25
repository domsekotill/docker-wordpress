# syntax = docker/dockerfile:1.0-experimental

ARG nginx_version=latest
FROM nginx:${nginx_version} as nginx
LABEL uk.org.kodo.maintainer = "Dom Sekotill <dom.sekotill@kodo.org.uk>"
COPY nginx.conf /etc/nginx/conf.d/default.conf


FROM php:7.3-fpm as deps
RUN apt-get update \
 && apt-get install -y \
    bash-builtins \
    libgmp10 \
    libjpeg62 \
    libpng16-16 \
    libzip4 \
    rsync \
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

ARG wp_version=latest
WORKDIR /app
VOLUME /app/wp-content
ENV WORDPRESS_ROOT=/app

ADD https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    /usr/local/lib/wp-cli.phar
COPY wp.sh /usr/local/bin/wp
COPY --from=compile /usr/local/etc/php /usr/local/etc/php
COPY --from=compile /usr/local/lib/php /usr/local/lib/php
RUN wp core download --skip-content --locale=en_GB --version=${wp_version} \
 && rm wp-config-sample.php \
 && mkdir --mode=go+w media \
 && mkdir -p wp-content/mu-plugins \
 && curl https://raw.githubusercontent.com/Ayesh/WordPress-Password-Hash/1.5.1/wp-php-password-hash.php \
  > wp-content/mu-plugins/password-hash.php \
 &&:

COPY opcache.ini /usr/local/etc/php/conf.d/opcache-recommended.ini
COPY entrypoint.sh /bin/entrypoint

# PAGER is used by the wp-cli tool, the default 'less' is not installed
ENV PAGER=more

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
