apt-get update
apt install python3 -y
apt install vim -y
apt install ansible -y
apt install pip -y
pip install netmiko
pip install paramiko
pip install prettytable

route add default gw 192.168.31.120
cp hosts /etc/ansible/hosts
