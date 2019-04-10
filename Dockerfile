ARG nginx_version=latest
FROM nginx:${nginx_version}

LABEL uk.org.kodo.maintainer = "Dom Sekotill <dom.sekotill@kodo.org.uk>"

COPY nginx.conf /etc/nginx/conf.d/default.conf
