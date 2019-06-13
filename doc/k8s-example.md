Kubernetes
==========

This document outlines how to run Wordpress as a Kubernetes Deployment.

It is assumed that there is an [ingress controller][] already configured for 
the cluster, and that the reader is familiar with tasks such as provisioning 
a TLS certificate and a PersistentVolume to back the PersistentVolumeClaim.

The complete example YAML file which goes with this document is 
[k8s-example.yml](k8s-example.yml).


Configuration
-------------

Sensitive information like the database credentials and TLS certificate key 
should go into Secrets, while all other [configuration 
values](configuration.md) can be placed into ConfigMaps.  As the 
configuration files under **/etc/wordpress** can be nested in subdirectories 
there is no problem mounting multiple Secrets and ConfigMaps.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  plugins.txt: |
    cache-control
    wp-mail-smtp
    wp-statistics
  wordpress.conf: |
    THEMES=( twentyeighteen twentynineteen )
    LANGUAGES+=( en_GB fr_FR de_DE )

---

apiVersion: v1
kind: Secret
metadata:
  name: my-app-mysql-pass
data:
  mysql.conf: |
    REJfSE9TVD1teXNxbC5leGFtcGxlLmNvbQpEQl9OQU1FPWV4YW1wbGVfZGIKREJfVVNFUj1leGFt
    cGxlX3VzZXIKREJfUEFTUz1aWGhoYlhCc1pWQmhjM04zYjNKa0NnCg==
```


Deployment
----------

The author recommends managing Pods with Deployments.

### Static Files Volume

The two containers which make up a Wordpress Pod (FastCGI server and HTTP 
server) need to share static files which the FastCGI server (which contains 
the Wordpress core, plugin and theme files) has, but which the HTTP server 
needs to serve.  This volume does not need to be persistent, so can be of 
the 'emptyDir' type:

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  containers:
  - name: fastcgi
    volumeMounts:
    - name: static
      mountPath: /app/static

  - name: http
    volumeMounts:
    - name: static
      mountPath: /app/static

  volumes:
  - name: static
    emptyDir: {}
```

### User Uploads Volume

All content that users upload to Wordpress goes into a tree within 
**/app/media**, which must be a persistent volume mounted in both 
containers.  This volume is requested through a PersistentVolumeClaim:

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  containers:
  - name: fastcgi
    volumeMounts:
    - name: media
      mountPath: /app/media

  - name: http
    volumeMounts:
    - name: media
      mountPath: /app/media

  volumes:
  - name: media
    persistentVolumeClaim:
      claimName: my-app-media

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-app-media
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: ""
  resources:
    requests:
      storage: 5Gi
```

### Readiness Probe

Prior to staring the FastCGI server the Wordpress image downloads and 
installs plugins, themes, and language packs, then populates the shared 
static files volume.  This takes some time so a readiness probe checking for 
the FastCGI port (9000) is needed:

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  containers:
  - name: fastcgi
    readinessProbe:
      periodSeconds: 60
      tcpSocket:
        port: 9000
```

### Final

Putting it all together, the complete Deployment for running a single 
instance of a Pod with the two containers:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: fastcgi
        image: docker.kodo.org.uk/singing-chimes.co.uk/wordpress/fastcgi:latest
        imagePullPolicy: Always
        volumeMounts:

        # Keep MySQL credentials in a Secret
        - name: mysql-pass
          mountPath: /etc/wordpress/secret

        # Rest of the config
        - name: config
          mountPath: /etc/wordpress

        # Shared non-persistent volume
        - name: static
          mountPath: /app/static

        # Shared persistent user-media volume
        - name: media
          mountPath: /app/media

        readinessProbe:
          periodSeconds: 5
          tcpSocket:
            port: 9000

      - name: http
        image: docker.kodo.org.uk/singing-chimes.co.uk/wordpress/nginx:latest
        imagePullPolicy: Always
        volumeMounts:
        - name: static
          mountPath: /app/static
        - name: media
          mountPath: /app/media

      volumes:
      - name: mysql-pass
        secret:
          secretName: my-app-mysql-pass
      - name: config
        configMap:
          name: my-app-config
      - name: static
        emptyDir: {}
      - name: media
        persistentVolumeClaim:
          claimName: my-app-media
```


Service and Ingress
-------------------

To expose the Wordpress instance publicly we need a Service and Ingress. The 
Ingress acts as the TLS termination for the website.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
  ports:
  - name: http
    protocol: TCP
    port: 80

---

apiVersion: v1
kind: Secret
type: kubernetes.io/tls
metadata:
  name: my-app-cert
data:
  tls.crt: …
  tls.key: …

---

apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: my-app
  annotations:
    nginx.org/hsts: True
spec:
  tls:
  - hosts: [my-app.co.uk]
    secretName: my-app-cert

  rules:
  - host: my-app.co.uk
    http:
      paths:
      - path: /
        backend:
          serviceName: my-app
          servicePort: http
```


[ingress controller]:
  https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/
  "Kubernetes.io Ingress Controllers"
