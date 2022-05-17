#!/bin/bash

status_enable_openvpn=$(systemctl is-enabled openvpn.service)
status_enable_wpa_supplicant=$(systemctl is-enabled wpa_supplicant.service)
status_enable_mariadb=$(systemctl is-enabled mariadb.service)
status_enable_mysql=$(systemctl is-enabled mysql.service)
status_enable_nginx=$(systemctl is-enabled nginx.service)
status_enable_rabbitmq_server=$(systemctl is-enabled rabbitmq-server.service)
status_enable_rabbit_consumer=$(systemctl is-enabled rabbit-consumer.service)
status_enable_pyshake=$(systemctl is-enabled pyshake.service)
status_enable_pm2_pi=$(systemctl is-enabled pm2-pi.service)

status_active_openvpn=$(systemctl is-active openvpn.service)
status_active_wpa_supplicant=$(systemctl is-active wpa_supplicant.service)
status_active_mariadb=$(systemctl is-active mariadb.service)
status_active_mysql=$(systemctl is-active mysql.service)
status_active_nginx=$(systemctl is-active nginx.service)
status_active_rabbitmq_server=$(systemctl is-active rabbitmq-server.service)
status_active_rabbit_consumer=$(systemctl is-active rabbit-consumer.service)
status_active_pyshake=$(systemctl is-active pyshake.service)
status_active_pm2_pi=$(systemctl is-active pm2-pi.service)

echo "openvpn          : $status_enable_openvpn $status_active_openvpn"
echo "wpa_supplicant   : $status_enable_wpa_supplicant $status_active_wpa_supplicant"
echo "mariadb          : $status_enable_mysql $status_active_mariadb"
echo "mysql            : $status_enable_mysql $status_active_mysql"
echo "nginx            : $status_enable_nginx $status_active_nginx"
echo "rabbitmq-server  : $status_enable_rabbitmq_server $status_active_rabbitmq_server"
echo "rabbit-consumer  : $status_enable_rabbit_consumer $status_active_rabbit_consumer"
echo "pyshake          : $status_enable_pyshake $status_active_pyshake"
echo "pm2-pi           : $status_enable_pm2_pi $status_active_pm2_pi"
