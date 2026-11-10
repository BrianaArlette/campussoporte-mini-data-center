#!/bin/bash
# Se ejecuta una sola vez, cuando MariaDB inicializa su volumen.
# Contraseñas de .env para laboratorio local: evitar comillas simples y espacios.
set -e
mariadb --protocol=socket -uroot -p"${MARIADB_ROOT_PASSWORD}" <<-EOSQL
  CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY '${APP_DB_PASSWORD}';
  GRANT SELECT, INSERT, UPDATE, DELETE ON dc_app.* TO 'app_user'@'%';
  CREATE USER IF NOT EXISTS 'grafana_ro'@'%' IDENTIFIED BY '${GRAFANA_DB_PASSWORD}';
  GRANT SELECT ON dc_app.* TO 'grafana_ro'@'%';
  FLUSH PRIVILEGES;
EOSQL
echo '[CampusSoporte] usuarios app_user y grafana_ro configurados.'
