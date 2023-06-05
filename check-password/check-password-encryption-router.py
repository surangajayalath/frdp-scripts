#!/usr/bin/env python

import socket
from telnetlib import Telnet
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

# Create a DataLoader object to load the inventory data
loader = DataLoader()

# Create an InventoryManager object with the loader and specify the inventory file
inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])

# Iterate over each host in the 'routers' group of the inventory
for host in inventory.get_hosts('routers'):
    # Get the necessary variables for Telnet connection from the host
    ansible_host = host.get_vars()['ansible_host']
    ansible_user = host.get_vars()['ansible_user']
    ansible_password = host.get_vars()['ansible_password']
    enable_password = host.get_vars()['ansible_enable']

    # Define a function to connect to the host using Telnet and retrieve information
    def show_users_telnet():
        # Connect to the host using Telnet
        tn = Telnet(ansible_host)

        # Wait for the 'Username:' prompt and send the ansible_user
        tn.read_until(b'Username: ')
        tn.write(ansible_user.encode('ascii') + b'\n')

        # Wait for the 'Password:' prompt and send the ansible_password
        tn.read_until(b'Password: ')
        tn.write(ansible_password.encode('ascii') + b'\n')

        # Wait for the command prompt and send the command to show password encryption status
        tn.read_until(b'#')
        tn.write(b'show run | include service password-encryption\n')

        # Read the output until the command prompt and decode it as UTF-8
        stdout = tn.read_until(b'#').decode('utf-8')

        # Split the output into lines
        lines = stdout.split('\n')

        # Print a separator line
        print("----------------------------------------------------------")

        # Iterate over each line in the output
        for line in lines:
            # Check if the line contains the text 'no service password-encryption'
            if 'no service password-encryption' in line:
                print("Password encryption is not available. Enabling it...")
                enable_password_encryption(tn)
                break
        else:
            # If the loop completes without encountering the 'break' statement,
            # it means that password encryption is enabled
            print("Password encryption is enabled.")
            print(stdout)

    def enable_password_encryption(tn):

        # Send the command to enable password encryption
        tn.write(b'configure terminal\n')
        tn.read_until(b'#')
        tn.write(b'service password-encryption\n')
        tn.read_until(b'#')


        # Print a message indicating successful encryption
        print("Password encryption enabled successfully.")

    # Call the function to retrieve the output from the Telnet connection
    show_users_telnet()

