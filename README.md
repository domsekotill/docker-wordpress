Wordpress for Docker
====================

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


[^1]: In a future release Simple Storage Service (S3) services may be 
  supported out-of-the-box.

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

**Note:** Building manually requires Docker 17.05 or later.

To build the PHP-FPM image run:

```shell
docker build -t wordpress:tag .
```

To build the Nginx companion image, run:

```shell
docker build -t wordpress-nginx:tag --target=nginx .
```