FROM pgbouncer/pgbouncer:latest

COPY pgbouncer/entrypoint.sh /entrypoint.sh
COPY pgbouncer/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini
COPY pgbouncer/auth.txt /auth.txt

ENTRYPOINT ["/entrypoint.sh"]