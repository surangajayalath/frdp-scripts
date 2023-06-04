#!/usr/bin/env python

import socket
from telnetlib import Telnet
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

# Create a DataLoader instance
loader = DataLoader()

# Create an InventoryManager instance and load inventory from '/etc/ansible/hosts'
inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])

# Iterate over hosts in the 'switch' group
for host in inventory.get_hosts('switch'):
    # Get the Ansible variables for the host
    ansible_host = host.get_vars()['ansible_host']
    ansible_user = host.get_vars()['ansible_user']
    ansible_password = host.get_vars()['ansible_password']
    enable_password = host.get_vars()['ansible_enable']

    # Define a function to perform Telnet and show IP routes
    def show_users_telnet():
        # Create a Telnet instance for the host
        tn = Telnet(ansible_host)

        # Perform Telnet authentication
        tn.read_until(b'Username: ')
        tn.write(ansible_user.encode('ascii') + b'\n')

        tn.read_until(b'Password: ')
        tn.write(ansible_password.encode('ascii') + b'\n')

        # Execute 'show ip route' command
        tn.read_until(b'#')
        tn.write(b'show ip route\n')

        # Read the command output and decode it as UTF-8
        stdout = tn.read_until(b'#').decode('utf-8')
        lines = stdout.split('\n')

        # Print each line of the output
        for line in lines:
            print(line)

        return lines

    # Call the show_users_telnet function to execute Telnet and show IP routes
    show_users_telnet()
