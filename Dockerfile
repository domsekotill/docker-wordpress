FROM php:7.3-fpm

LABEL uk.org.kodo.maintainer "Dom Sekotill <dom.sekotill@kodo.org.uk>"

# From the official wordpress docker file (modified):
# ----
# install the PHP extensions we need
RUN apt-get update && apt-get install -y \
		libgmp-dev \
		libjpeg-dev \
		libpng-dev \
	&& rm -rf /var/lib/apt/lists/* \
	&& docker-php-ext-configure gd --with-png-dir=/usr --with-jpeg-dir=/usr \
	&& docker-php-ext-install gd mysqli opcache gmp

# set recommended PHP.ini settings
# see https://secure.php.net/manual/en/opcache.installation.php
RUN { \
		echo 'opcache.memory_consumption=128'; \
		echo 'opcache.interned_strings_buffer=8'; \
		echo 'opcache.max_accelerated_files=4000'; \
		echo 'opcache.revalidate_freq=60'; \
		echo 'opcache.fast_shutdown=1'; \
		echo 'opcache.enable_cli=1'; \
	} > /usr/local/etc/php/conf.d/opcache-recommended.ini
# ----

ARG wp_version
ARG wp_sha1=
ENV WORDPRESS_VERSION=${wp_version}

WORKDIR /app
VOLUME /app/wp-content
ENV WORDPRESS_ROOT=/app

ADD install.sh /install.sh
RUN /install.sh "${wp_version}" "${wp_sha1}" && rm /install.sh

COPY entrypoint.sh /bin/entrypoint

ENTRYPOINT ["/bin/entrypoint"]
CMD ["php-fpm"]
