#!/usr/bin/env python

# socket module is imported to provide low-level network communication.
import socket 
# Telnet class from telnetlib module is imported to establish a Telnet connection to the routers.
from telnetlib import Telnet 
# PrettyTable class from prettytable module is imported to create a well-formatted table for displaying information.
from prettytable import PrettyTable 
# InventoryManager class and DataLoader class from ansible.inventory.manager and ansible.parsing.dataloader modules are imported to manage Ansible inventory and load inventory data respectively.
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

loader = DataLoader() # loader is an instance of DataLoader used to load inventory data from Ansible.
inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts']) # inventory is an instance of InventoryManager used to manage the inventory and retrieve host information.

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
        tn.write(b'show ip int br\n')

        stdout = tn.read_until(b'#').decode('utf-8')
        lines = stdout.split('\n')

        # Filter lines with "up" status and "unassigned" ports
        up_lines = [line for line in lines if "up" in line and "unassigned" in line]

        # Extract information for each interface and display in table format
        table = PrettyTable(['Interface', 'IP Address', 'Method', 'Status', 'Protocol'])
        table.align = 'l' # set all fields to left align
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

    def shutdown_ports_telnet(ports):
        tn = Telnet(ansible_host)
        tn.read_until(b'Username: ')
        tn.write(ansible_user.encode('ascii') + b'\n')

        tn.read_until(b'Password: ')
        tn.write(ansible_password.encode('ascii') + b'\n')

        tn.read_until(b'#')
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
