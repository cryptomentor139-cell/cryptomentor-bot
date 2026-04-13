import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

# Get timestamps for a single user's scans
cmd = 'journalctl -u cryptomentor.service -n 5000 --no-pager | grep "\[Scalping:312485564\] Scan cycle" | tail -n 20'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
ssh.close()
