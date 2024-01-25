#!/bin/sh

sudo mount /var/log
sudo mount /home/pi
sudo mount /smartvending

sudo chmod 755 /var/log

if [ ! -d /var/log/smartvending ]; then
    sudo mkdir /var/log/smartvending
    sudo chown pi.pi /var/log/smartvending
    sudo chmod -Rf o+w /var/log/smartvending
fi

if [ ! -d /var/log/smartvending/server ]; then
    sudo mkdir /var/log/smartvending/server
    sudo chown pi.pi /var/log/smartvending/server
    sudo chmod -Rf o+w /var/log/smartvending/server
fi

if [ ! -d /var/log/smartvending/controller ]; then
    sudo mkdir /var/log/smartvending/controller
    sudo chown pi.pi /var/log/smartvending/controller
    sudo chmod -Rf o+w /var/log/smartvending/controller
fi

if [ ! -d /var/log/smartvending/system ]; then
    sudo mkdir /var/log/smartvending/system
    sudo chown pi.pi /var/log/smartvending/system
    sudo chmod -Rf o+w /var/log/smartvending/system
fi

if [ ! -L /smartvending/server/log ]; then
    if [ -d /smartvending/server/log ]; then
        sudo rm -Rf /smartvending/server/log
    fi
    
    sudo ln -s /var/log/smartvending/server /smartvending/server/log
fi

if [ ! -d /tmp/rfkill ]; then
    mkdir /tmp/rfkill
    #sudo chown -Rf pi.pi /var/run/systemd
    #sudo chmod -Rf o+w /var/run/systemd
fi

if [ ! -d /var/run/systemd ]; then
    sudo mkdir /var/run/systemd
    sudo mkdir /var/run/systemd/rfkill
    sudo chown -Rf pi.pi /var/run/systemd
    sudo chmod -Rf o+w /var/run/systemd
fi

# Create Nginx run dir
if [ ! -d /var/run/nginx ]; then
    sudo mkdir /var/run/nginx
    sudo chown pi.pi /var/run/nginx
    sudo chmod -Rf o+w /var/run/nginx
fi

# Create Rabbitmq log dir
if [ ! -d /var/log/rabbitmq ]; then
    sudo mkdir /var/log/rabbitmq
    sudo chown pi.pi /var/log/rabbitmq
    sudo chmod -Rf o+w /var/log/rabbitmq
fi

# Create Mysql log dir
if [ ! -d /var/log/mysql ]; then
    sudo mkdir /var/log/mysql
    sudo chown pi.pi /var/log/mysql
    sudo chmod -Rf o+w /var/log/mysql
fi

# Create Shakecontroller log dir
if [ ! -d /var/log/shakecontroller ]; then
    sudo mkdir /var/log/shakecontroller
    sudo chown pi.pi /var/log/shakecontroller
    sudo chmod -Rf o+w /var/log/shakecontroller
fi

# Create Nginx log dir
if [ ! -d /var/log/nginx ]; then
    sudo mkdir /var/log/nginx
    sudo chown pi.pi /var/log/nginx
    sudo chmod -Rf o+w /var/log/nginx
fi

mkdir /var/run/nginx/client_body_temp
mkdir /var/run/nginx/fastcgi_temp
mkdir /var/run/nginx/passenger_temp
mkdir /var/run/nginx/scgi_temp
mkdir /var/run/nginx/uwsgi_temp
mkdir /var/run/nginx/proxy_temp

sudo unlock-system
if [ ! -L /opt/nginx/client_body_temp ]; then
    sudo ln -s /var/run/nginx/client_body_temp /opt/nginx/client_body_temp
fi

if [ ! -L /opt/nginx/fastcgi_temp ]; then
    sudo ln -s /var/run/nginx/fastcgi_temp /opt/nginx/fastcgi_temp
fi

if [ ! -L /opt/nginx/passenger_temp ]; then
    sudo ln -s /var/run/nginx/passenger_temp /opt/nginx/passenger_temp
fi

if [ ! -L /opt/nginx/scgi_temp ]; then
    sudo ln -s /var/run/nginx/scgi_temp /opt/nginx/scgi_temp
fi

if [ ! -L /opt/nginx/uwsgi_temp ]; then
    sudo ln -s /var/run/nginx/uwsgi_temp /opt/nginx/uwsgi_temp
fi

if [ ! -L /opt/nginx/proxy_temp ]; then
    sudo ln -s /var/run/nginx/proxy_temp /opt/nginx/proxy_temp
fi

if [ ! -L /smartvending/server/public/storage ]; then
    ln -s /smartvending/server/storage /smartvending/server/public/
fi

sudo lock-system






