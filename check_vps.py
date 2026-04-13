import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

cmd = 'cd /root/cryptomentor-bot && git remote -v'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))

ssh.close()
