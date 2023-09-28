FROM clickhouse/clickhouse-server
COPY entrypoint /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint"]