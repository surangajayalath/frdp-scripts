#!/usr/bin/env python

import socket
from telnetlib import Telnet
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

loader = DataLoader()
inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])

for host in inventory.get_hosts('routers'):
    ansible_host = host.get_vars()['ansible_host']
    ansible_user = host.get_vars()['ansible_user']
    ansible_password = host.get_vars()['ansible_password']
    enable_password = host.get_vars()['ansible_enable']

    def show_users_telnet():
        tn = Telnet(ansible_host)

        tn.read_until(b'Username: ')
        tn.write(ansible_user.encode('ascii') + b'\n')

        tn.read_until(b'Password: ')
        tn.write(ansible_password.encode('ascii') + b'\n')

        tn.read_until(b'#')
        tn.write(b'show ip route\n')

        stdout = tn.read_until(b'#').decode('utf-8')
        lines = stdout.split('\n')

        # Print the lines directly
        for line in lines:
            print(line)

        return lines

    # Call the show_users_telnet function
    show_users_telnet()
