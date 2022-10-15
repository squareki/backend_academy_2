apt-get update
apt-get install -y libsasl2-dev python3-dev libldap2-dev libssl-dev python3-pip python-setuptools git
apt-get install -y mysql-server mysql-client

cd /opt
git clone https://github.com/linkedin/oncall.git
cd oncall

python3 setup.py develop
pip3 install -e '.[dev]'

service mysql start
mysql -u root < ./db/schema.v0.sql
echo "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '1234'; FLUSH PRIVILEGES;" | mysql -u root

cat << EOF > /lib/systemd/system/oncall.service

[Unit]
Description=Oncall service

[Service]
ExecStart=/usr/local/bin/oncall-dev /opt/oncall/configs/config.yaml

[Install]
WantedBy=multi-user.target

EOF

apt-get install systemctl
systemctl daemon-reload
systemctl enable oncall.service 
systemctl start oncall.service 