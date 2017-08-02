#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install postgresql postgresql-server-dev-all postgresql-client python-psycopg2
sudo service postgresql start
sudo -u postgres psql -c 'create database deephack'
sudo -u postgres psql -c "CREATE USER deephack WITH PASSWORD 'deephack';"
sudo -u postgres psql -c 'alter database deephack owner to deephack'
pg_hba="/etc/postgresql/9.5/main/pg_hba.conf"
if ! sudo grep -Fxq "deephack" $pg_hba; then
    cat <<EOF | sudo tee $pg_hba
local   all             postgres                                peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
# very secure k?
local deephack deephack trust
EOF
    sudo service postgresql reload
fi
