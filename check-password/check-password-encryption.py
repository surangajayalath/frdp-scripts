#!/usr/bin/env python

import socket
from telnetlib import Telnet
from prettytable import PrettyTable
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
        tn.write(b'show run | include service password-encryption\n')

        stdout = tn.read_until(b'#').decode('utf-8')
        lines = stdout.split('\n')

        print("----------------------------------------------------------")

        for line in lines:
            if 'no service password-encryption' in line:
                print("Password encryption is not available.")
                break
        else:
            print("Password encryption is enabled.")
            print(stdout)

    # Get list of open ports
    up_lines = show_users_telnet()
    ports = [line.split()[0] for line in up_lines] if up_lines else []
