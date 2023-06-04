#!/usr/bin/env python

import socket
from telnetlib import Telnet
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

# Create a data loader object for Ansible
loader = DataLoader()

# Initialize the inventory manager with the loader and specify the inventory source file
inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])

# Iterate over hosts in the 'routers' group from the inventory
for host in inventory.get_hosts('routers'):
    # Extract required variables for Telnet connection from host variables
    ansible_host = host.get_vars()['ansible_host']
    ansible_user = host.get_vars()['ansible_user']
    ansible_password = host.get_vars()['ansible_password']
    enable_password = host.get_vars()['ansible_enable']

    # Define a function to perform Telnet operations and show ARP table
    def show_users_telnet():
        # Connect to the host using Telnet
        tn = Telnet(ansible_host)

        # Read the output until prompted for the username and send the username
        tn.read_until(b'Username: ')
        tn.write(ansible_user.encode('ascii') + b'\n')

        # Read the output until prompted for the password and send the password
        tn.read_until(b'Password: ')
        tn.write(ansible_password.encode('ascii') + b'\n')

        # Read the output until the command prompt and send the 'show arp' command
        tn.read_until(b'#')
        tn.write(b'show arp\n')

        # The decode('utf-8') part is used to convert the bytes received from the Telnet connection into a human-readable string format using the UTF-8 encoding.
        stdout = tn.read_until(b'#').decode('utf-8')

        # Split the output into lines
        lines = stdout.split('\n')

        # Print the output
        print(stdout)

    # Call the defined function to show ARP table via Telnet
    up_lines = show_users_telnet()

    # Extract the list of open ports from the Telnet output
    ports = [line.split()[0] for line in up_lines] if up_lines else []

    # Print the list of open ports
    print(ports)
