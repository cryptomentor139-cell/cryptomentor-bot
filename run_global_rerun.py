import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

cmd = 'cd /root/cryptomentor-bot && ./venv/bin/python3 global_rerun.py'
stdin, stdout, stderr = ssh.exec_command(cmd)
output = stdout.read().decode('utf-8', errors='ignore')
error = stderr.read().decode('utf-8', errors='ignore')

with open('rerun_log.txt', 'w', encoding='utf-8') as f:
    f.write(output)
    f.write("\n--- ERRORS ---\n")
    f.write(error)

ssh.close()
print("Global rerun execution finished. Results saved to rerun_log.txt")
