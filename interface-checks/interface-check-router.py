#!/usr/bin/env python

import socket
from telnetlib import Telnet
from prettytable import PrettyTable
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

# Create a data loader and inventory manager for Ansible
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])

# Iterate over each host in the 'routers' group
for host in inventory.get_hosts('routers'):
    ansible_host = host.get_vars()['ansible_host']
    ansible_user = host.get_vars()['ansible_user']
    ansible_password = host.get_vars()['ansible_password']
    enable_password = host.get_vars()['ansible_enable']

    # Establish a Telnet connection to the current host
    tn = Telnet(ansible_host)
    tn.read_until(b'Username: ')
    tn.write(ansible_user.encode('ascii') + b'\n')
    tn.read_until(b'Password: ')
    tn.write(ansible_password.encode('ascii') + b'\n')
    tn.read_until(b'#')

    # Function to show the IP interfaces and their status
    def show_users_telnet():
        tn.write(b'show ip int br\n')
        stdout = tn.read_until(b'#').decode('utf-8')
        lines = stdout.split('\n')

        # Filter lines with "up" status and "unassigned" ports
        up_lines = [line for line in lines if "up" in line and "unassigned" in line]

        # Extract information for each interface and display in table format
        table = PrettyTable(['Interface', 'IP Address', 'Method', 'Status', 'Protocol'])
        table.align = 'l'  # set all fields to left align
        for line in up_lines:
            interface, ip_address, _, method, status, protocol = line.split()
            table.add_row([interface, ip_address, method, status, protocol])

        # Print table
        if not table._rows:
            print(stdout)
            print()
            return None
        else:
            print(table)
            return up_lines

    # Function to shutdown the specified ports
    def shutdown_ports_telnet(ports):
        tn.write(b'configure terminal\n')
        for port in ports:
            tn.read_until(b'#')
            tn.write(f'interface {port}\n'.encode('ascii'))
            tn.write(b'shutdown\n')

        tn.read_until(b'#')
        tn.write(b'end\n')
        tn.write(b'exit\n')

        stdout = tn.read_all().decode('utf-8')
        print(stdout)

    # Get list of open ports
    up_lines = show_users_telnet()
    ports = [line.split()[0] for line in up_lines] if up_lines else []

    # Check if there are open ports
    if not ports:
        print(f"There are no ports up on {ansible_host}.")
        print()
    else:
        # Call the shutdown_ports_telnet function with the list of open ports
        shutdown_ports_telnet(ports)
        print(f"Ports have been shut down on {ansible_host}.")

    # Close the Telnet connection for the current host
    tn.close()
