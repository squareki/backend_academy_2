FROM prom/prometheus

# ADD prometheus.yml /etc/prometheus/
# COPY prometheus.yml /etc/prometheus/prometheus.yml

# ENTRYPOINT [ "/usr/local/bin/prometheus", "--config.file=/etc/prometheus/prometheus.yaml",]
# ENTRYPOINT [ "/usr/local/bin/prometheus", "--config.file", "/etc/prometheus/config.yaml", "--storage.tsdb.path", "/var/lib/prometheus/", "--web.console.templates=/etc/prometheus/consoles", "--web.console.libraries=/etc/prometheus/console_libraries"]