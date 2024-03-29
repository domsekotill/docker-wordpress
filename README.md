Wordpress for Docker
====================

[![gitlab-ico]][gitlab-link]
[![github-ico]][github-link]
[![licence-mpl20]](/COPYING)
[![pipeline-status]][pipeline-report]

Docker images for Wordpress.

The primary aim is to be secure and easy to deploy.  Unlike other Wordpress 
images the statefulness is reduced to the bare minimum; aside from the 
required database only the uploaded media directory needs to be persistent, 
and even that can be avoided with a media cloud storage plugin[^1].

Two images are produced from the Dockerfile:

-   The primary runs a PHP server with a FastCGI (port 9000) interface 
    ([PHP-FPM][]), with Wordpress installed.

-   The second image runs Nginx with an HTTP (port 80) interface, which 
    serves all the static files and proxies non-static requests to the 
    PHP-FPM server.


[php-fpm]: https://php-fpm.org/


Usage
-----

Typical usage requires both images be run in containers on the same host, 
sharing a volatile (non-persistent) volume containing the static files, 
mounted at */app/static*. This volume is populated by the PHP-FPM container 
during its startup.

The containers share another persistent volume for user-uploaded media files 
(if no media cloud storage plugin is used) mounted at */app/media*.

The nginx container is not intended to be publicly accessible (it only 
listens on port 80).  Some form of HTTPS termination is required at 
a minimum.

See the [configuration document](/doc/configuration.md) for an explanation 
of the configuration files and the available options.

See the [Kubernetes example document](/doc/k8s-example.md) to see an example 
deployment of pods running these services.


Build
-----

> **Note:** Building manually requires Docker 18.09 or later with the 
> [Buildkit][] feature enabled.

> **Note:** *(Dec 2020)* Currently WP-CLI does not support PHP-8. Likely various plugins and
> themes also do not work with PHP-8. Therefore until wider support is available, supply
> a PHP-7 version with a build argument.

To build the PHP-FPM image run:

```shell
DOCKER_BUILDKIT=1 docker build -t wordpress:tag --build-arg php_version=7.4.13 .
```

To build the Nginx companion image, run:

```shell
DOCKER_BUILDKIT=1 docker build -t wordpress-nginx:tag --target=nginx .
```


---

[^1]: In a future release Simple Storage Service (S3) services may be 
  supported out-of-the-box.

[buildkit]:
  https://docs.docker.com/develop/develop-images/build_enhancements/
  "Build Enhancements for Docker"

[gitlab-ico]:
  https://img.shields.io/badge/GitLab-code.kodo.org.uk-blue.svg?logo=gitlab
  "GitLab"

[gitlab-link]:
  https://code.kodo.org.uk/singing-chimes.co.uk/wordpress
  "Go to the project at code.kodo.org.uk"

[github-ico]:
  https://img.shields.io/badge/GitHub-domsekotill/docker--wordpress-blue.svg?logo=github
  "GitHub"

[github-link]:
  https://github.com/domsekotill/docker-wordpress
  "Go to the project at github.com"

[licence-mpl20]:
  https://img.shields.io/badge/License-MPL--2.0-blue.svg
  "Licence: Mozilla Public License 2.0"

[pipeline-status]:
  https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/badges/main/pipeline.svg

[pipeline-report]:
  https://code.kodo.org.uk/singing-chimes.co.uk/wordpress/pipelines?ref=main
  "Pipelines"
