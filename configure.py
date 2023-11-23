from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios_telnet',
    'ip': '172.16.197.128',
    'port': 5000
}

net_connect = ConnectHandler(**device)

config_commands = [
    "hostname KICD-Switch",
    "enable secret password",
    "no ip domain-lookup",
    "exit",
    "config",
    'vlan 10',
    'name Voice',
    'exit',
    'vlan 11',
    'name Wireless',
    'exit',
    'interface vlan 1',
    'ip address 10.10.10.1 255.255.255.0',
    'exit',
    'interface vlan 10',
    'ip address 10.10.20.1 255.255.255.0',
    'exit',
    'interface vlan 11',
    'ip address 10.10.30.1 255.255.255.0',
    'exit',
    'ip dhcp pool voice-pool',
    'network 10.10.20.0 /24',
    'default-router 10.10.20.1',
    'ip dhcp pool wireless-pool',
    'network 10.10.10.0 /24',
    'default-router 10.10.30.1',
    'ip routing',
    'interface Ethernet0/0',
    'no shutdown',
    'switchport mode access',
    'switchport access vlan 10',
    'exit',
    'interface Ethernet0/1',
    'switchport mode access',
    'switchport access vlan 11',
    'no shutdown',
    'exit',
    "do sh ip int br",
    "do sh run"
]

output = net_connect.send_config_set(config_commands)

print(output)

net_connect.disconnect()
