import paramiko
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

cmd = 'journalctl -u cryptomentor.service -n 5000 --no-pager | grep ETHUSDT'
stdin, stdout, stderr = ssh.exec_command(cmd)
data = stdout.read().decode('utf-8', errors='ignore')
sys.stdout.buffer.write(data.encode('utf-8'))
ssh.close()
