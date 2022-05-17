import os
import sys
import json
import requests
from datetime import datetime


ROUTER_IPADDR = '192.168.1.1'

payload = {
    'username': 'admin',
    'passwd': 'c3284d0f94606de1fd2af172aba15bf3'
}

# User param: router param
params_mapping = {
    'ccid': 'ccid',
    'imei': 'imei',
    'isp': 'isp',
    'network_name': 'network_name',
    'network_id': 'network_id',
    'network_channel': 'network_channel',
    'network_band': 'network_band',
    'device_model': 'device_model',
    'signal_quality': 'signal_quality',
    '4g_data_usage': 'data'
}


def is_router_online(ip_addr: str) -> bool:
    ping_param = '-c 1'
    timeout_param = '-w2'
    output_null_direction = ' > /dev/null 2>&1'

    # Ping remote address
    if os.system('ping ' + ping_param + ' ' + timeout_param + ' ' + ip_addr + output_null_direction) == 0:
        return True
    else:
        return False


def format_4g_data_usage(raw_data_usage: dict) -> dict:
    MAX_RECORD_CNT = 10

    ret_data_usage = {}
    list_days = raw_data_usage['days']
    list_days.sort(key=lambda date: datetime.strptime(date, "%Y-%m-%d"), reverse=True)
    list_days = list_days[0:MAX_RECORD_CNT]
    # print("list_days:", list_days)

    list_data = raw_data_usage['data']
    for __day in list_days:
        for __data in list_data:
            if __day == __data['date']:
                ret_data_usage[__day] = __data['total_4g']
                break

    return ret_data_usage


def get_args() -> list:
    ret_args = None
    if len(sys.argv) > 1:
        all_params = ''
        for index in range(1, len(sys.argv)):
            all_params += sys.argv[index].strip()

        ret_args = all_params.split(',')

        # Check if the argument is valid
        for parameter in ret_args:
            if parameter not in params_mapping:
                print("Error: Unknown parameter", parameter)
                print("")
                ret_args = None
                break

    return ret_args


def display_usage():
    print("====================================================")
    print("               svm-get-router-stat                  ")
    print("                     HS@2022                        ")
    print("====================================================")
    print("Usage: svm-get-router-stat.sh [param1],[param2],..[param_n]")
    print("e.g: svm-get-router-stat.sh ccid,signal_quality")
    print("")
    print("params             Details")
    print("======             =======")
    print("ccid             : SIM card id")
    print("imei             : Router imei")
    print("isp              : Internet service provider")
    print("network_name     : Network name")
    print("network_id       : Network id")
    print("network_channel  : Network channel")
    print("network_band     : Network band")
    print("device_model     : Router model")
    print("signal_quality   : 4G signal quality (in percentage)")
    print("4g_data_usage    : Recent mobile data usage (in byte)")
    print("dhcp_lease       : Current DHCP lease information")
    print("lan_port         : Current LAN port status")
    print("")


if __name__ == '__main__':

    args = get_args()
    # print(args)
    if args is not None:
        if is_router_online(ROUTER_IPADDR):
            ret_response_value: dict = {}
            login_req = requests.post('http://' + ROUTER_IPADDR + '/api/login', data=payload)
            
            if "Not Found" in login_req:
                print("Error: Unable to retrieve data from router")
                exit()
                
            login_req_response = json.loads(login_req.text)
            session_token = login_req_response['token']

            network_info_req = requests.get('http://' + ROUTER_IPADDR + '/api/network?action=list&dev=wwan0&token=' + session_token + '&_=1643135948017')
            network_info_req_response = json.loads(network_info_req.text)
            # print(network_info_req_response)

            data_usage_req = requests.get('http://' + ROUTER_IPADDR + '/data/flow.json?token=' + session_token + '&_=1643135948017')
            data_usage_req_response = json.loads(data_usage_req.text)
            # print(data_usage_req_response)

            # http://192.168.1.1/api/network?action=dhcp_lease&token=04b4920313f6f46da266196f433e3f7f&_=1647302795382
            dhcp_lease_req = requests.get('http://' + ROUTER_IPADDR + '/api/network?action=dhcp_lease&token=' + session_token + '&_=1643135948017')
            # dhcp_lease_req_response: [[{'expires': 4760, 'hostname': 'SVM77', 'ipaddr': '192.168.1.101', 'macaddr': 'e4-5f-01-6b-95-31'}], []]
            dhcp_lease_req_response = json.loads(dhcp_lease_req.text)
            #print("dhcp_lease_req_response:", dhcp_lease_req_response)

            # http://192.168.1.1/api/network?action=list&dev=lan&token=04b4920313f6f46da266196f433e3f7f&_=1647302940972
            lan_port_info_req = requests.get('http://' + ROUTER_IPADDR + '/api/network?action=list&dev=lan&token=' + session_token + '&_=1643135948017')
            # lan_port_info_req_response: {'code': 1, 'exist': 'yes', 'id': 'lan', 'ifname': 'eth1', 'ipaddr': '192.168.1.1', 'is_up': 'true', 'link_dev': 'br-lan', 'macaddr': 'f8:5e:3c:25:33:d8', 'name': 'br-lan', 'netmask': '255.255.255.0', 'proto': 'static', 'rx_bytes': 14951175, 'rx_packets': 68067, 'tx_bytes': 81408860, 'tx_packets': 152018, 'type': 'bridge', 'uptime': 49111}
            lan_port_info_req_response = json.loads(lan_port_info_req.text)
            # print("lan_port_info_req_response:", lan_port_info_req_response)

            # Populate data
            for param in args:
                if param == '4g_data_usage':
                    data_usage_req_response = format_4g_data_usage(data_usage_req_response)
                    ret_response_value[param] = data_usage_req_response
                else:
                    if param in network_info_req_response:
                        ret_response_value[param] = str(network_info_req_response[params_mapping[param]])
                    else:
                        ret_response_value[param] = ""

            if len(ret_response_value) > 0:
                print(ret_response_value)

        else:
            print("Error: Router not found")
    else:
        display_usage()
