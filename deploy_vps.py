import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

commands = [
    'cd /root/cryptomentor-bot',
    'git fetch ajax',
    'git reset --hard ajax/master',
    'git clean -fd',
    'systemctl restart cryptomentor.service',
    'systemctl restart cryptomentor-web.service'
]

full_cmd = " && ".join(commands)
stdin, stdout, stderr = ssh.exec_command(full_cmd)

print("--- STDOUT ---")
print(stdout.read().decode('utf-8'))
print("--- STDERR ---")
print(stderr.read().decode('utf-8', errors='ignore'))

ssh.close()
