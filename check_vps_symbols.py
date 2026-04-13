import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

# Get last 1000 lines of logs and filter for data fetching messages
cmd = 'journalctl -u cryptomentor.service -n 1000 --no-pager | grep "candles from Bitunix"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
ssh.close()
