INSTALL PLUGIN auth_socket SONAME 'auth_socket.so';

ALTER USER 'root'@'localhost' IDENTIFIED WITH auth_socket;
