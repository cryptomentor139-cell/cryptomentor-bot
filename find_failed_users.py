import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)

# Get logs from last 2 hours
cmd = 'journalctl -u cryptomentor.service --since "2 hours ago" --no-pager'
stdin, stdout, stderr = ssh.exec_command(cmd)
logs = stdout.read().decode('utf-8', errors='ignore')

# RegEx to find failures: [Scalping:7675185179] ETHUSDT - Order placement failed
failures = re.findall(r"\[Scalping:(\d+)\] (\w+) - Order placement failed", logs)

print(f"Found {len(failures)} failures.")
for user_id, symbol in failures:
    print(f"User {user_id} failed on {symbol}")

ssh.close()
