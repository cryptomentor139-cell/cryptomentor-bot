import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

# Search for ERROR or Exception in the last 5000 lines
cmd = 'journalctl -u cryptomentor.service -n 5000 --no-pager | grep -iE "error|exception|failed"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
ssh.close()
