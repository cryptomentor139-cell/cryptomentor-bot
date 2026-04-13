import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

# Chain commands to ensure directory changes persist
cmd_chain = " && ".join([
    'cd /root/cryptomentor-bot',
    'git fetch ajax',
    'git reset --hard ajax/master',
    'git clean -fd',
    'systemctl restart cryptomentor-web.service',
    'cd website-frontend',
    'npm install',
    'npm run build',
    'rm -rf /var/www/cryptomentor/*',
    'cp -r dist/* /var/www/cryptomentor/',
    'chown -R www-data:www-data /var/www/cryptomentor'
])

print(f"Executing chain...")
stdin, stdout, stderr = ssh.exec_command(f"export PATH=$PATH:/usr/bin:/usr/local/bin && {cmd_chain}")

print("--- STDOUT ---")
print(stdout.read().decode('utf-8'))
print("--- STDERR ---")
print(stderr.read().decode('utf-8', errors='ignore'))

ssh.close()
