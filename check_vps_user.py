import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

user_id = '7675185179'
cmd = f"journalctl -u cryptomentor.service -n 10000 --no-pager | grep -a '{user_id}' | tail -n 100"
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

ssh.close()
