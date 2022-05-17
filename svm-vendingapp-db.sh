#!/bin/bash

Usage() {
    echo "---------------------------------------------------"
    echo "|         Initialize Vendingapp Database          |"
    echo "---------------------------------------------------"
    echo "Usage: svn-vendingapp-db [OPTIONS]"
    echo ""
    echo "Option      Meaning"
    echo "-h|--help   Show this usage page"
    echo "-y|--yes    Auto-answer yes to any question"
    echo "-i|--init   Create and migrate vendingapp database"
    echo "--purge     !!! Warning !!! Delete vendingapp database"
    echo ""
    echo "Examples"
    echo "svn-vendingapp-db --init            :Init vendingapp database"
    echo "svn-vendingapp-db --init --purge    :Delete and Init vendingapp database"
    echo ""
    echo "Notes:"
    echo "Option '--yes' need to be used in conjunction with '--init' or '--purge' or both"    
    echo ""
}

Stop_All_Services() {
	systemctl stop rabbitmq-server.service
    systemctl stop rabbit-consumer.service
	systemctl stop pyshake.service
	sudo -u pi pm2 stop all
}

Start_mysql_services() {
    systemctl start mysql.service
}

Purge_Vendingapp_Db() {
	Stop_All_Services
    Start_mysql_services
	mysql -e "drop database vendingapp"
}

Initialize_Vendingapp_Db() {
	echo "Initializing vendingapp database..."
	sudo -u pi /usr/bin/bash -lc '(cd /smartvending/server && rails db:create)'
	sudo -u pi /usr/bin/bash -lc '(cd /smartvending/server && rails db:migrate)'
	sudo -u pi /usr/bin/bash -lc '(cd /smartvending/server && rails db:seed)'
    sudo -u pi /usr/bin/bash -lc '(cd /smartvending/server && rails startup:config)'
}

Run_Purge_Vendingapp_Db() {
	echo "!!! Warning !!! You're about to delete vendingapp database!"
	echo "!!! Warning !!! After deleted it'll be unrecoverable"
	
	
	user_input=""
	if [ "$1" = "auto-answer-yes" ]; then
		user_input="Yes"
		echo "!!! Warning !!! Are you sure you know what you're doing [Yes/no]? $user_input"
	else
		#read user_input
		read -p "!!! Warning !!! Are you sure you know what you're doing [Yes/no]? " user_input
	fi
	
	if [ "$user_input" = "Yes" ]; then
		echo "Purging vendingapp database..."
		Purge_Vendingapp_Db
	else
		echo ""
		echo "Bye."
		echo ""
		exit 0
	fi
}
  
 
is_purge_db="0"
is_init_db="0"
auto_answer_yes_key=""

for user_arg in "$@"
do
	if [ "$user_arg" = "-y" ] || [ "$user_arg" = "--yes" ]; then
		auto_answer_yes_key="auto-answer-yes"
	elif [ "$user_arg" = "-i" ] || [ "$user_arg" = "--init" ]; then
		is_init_db="1"
	elif [ "$user_arg" = "--purge" ]; then
		is_purge_db="1"
	else
		# Unknown option, show help page then exit
		Usage
		exit 0
	fi
done


if [ "$is_init_db" = "0" ] && [ "$is_purge_db" = "0" ]; then
	Usage
	exit 0
elif [ "$is_init_db" = "1" ] && [ "$is_purge_db" = "0" ]; then
	Initialize_Vendingapp_Db
elif [ "$is_init_db" = "0" ] && [ "$is_purge_db" = "1" ]; then
	Run_Purge_Vendingapp_Db "$auto_answer_yes_key"
elif [ "$is_init_db" = "1" ] && [ "$is_purge_db" = "1" ]; then
	Run_Purge_Vendingapp_Db "$auto_answer_yes_key"
	Initialize_Vendingapp_Db
else 
	Usage
fi

exit 0


