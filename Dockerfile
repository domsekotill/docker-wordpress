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

WORKDIR /app
VOLUME /app/wp-content
ENV WORDPRESS_ROOT=/app

ARG wp_version=latest
ARG wp_sha1=
ADD install.sh /install.sh
RUN /install.sh "${wp_version}" "${wp_sha1}" && rm /install.sh

COPY opcache.ini /usr/local/etc/php/conf.d/opcache-recommended.ini
COPY entrypoint.sh /bin/entrypoint

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
