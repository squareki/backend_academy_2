wget "https://github.com/prometheus/prometheus/releases/download/v2.37.0/prometheus-2.37.0.linux-amd64.tar.gz"

tar xvf prometheus-2.37.0.linux-amd64.tar.gz -C /tmp

cp /tmp/prometheus-2.37.0.linux-amd64/prometheus /usr/local/bin/
cp /tmp/prometheus-2.37.0.linux-amd64/promtool /usr/local/bin/

mkdir -p /etc/prometheus
mkdir /var/lib/prometheus

cp -r /tmp/prometheus-2.37.0.linux-amd64/consoles /etc/prometheus
cp -r /tmp/prometheus-2.37.0.linux-amd64/console_libraries /etc/prometheus

cat << EOF > /etc/prometheus/prometheus.yml
global:
    scrape_interval: 15s
scrape_configs:
    - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
        - targets: ['localhost:9090']
EOF

useradd --no-create-home --shell /bin/false prometheus

chown prometheus:prometheus -R /etc/prometheus
chown prometheus:prometheus -R /var/lib/prometheus/

cat << EOF > /lib/systemd/system/prometheus.service
[Unit]
Description=Prometheus service

[Service]
User=prometheus
Group=prometheus
ExecStart=/usr/local/bin/prometheus --config.file /etc/prometheus/prometheus.yml --storage.tsdb.path /var/lib/prometheus/ --web.console.templates=/etc/prometheus/consoles --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target

EOF

systemctl daemon-reload
systemctl enable prometheus.service
systemctl start prometheus.service