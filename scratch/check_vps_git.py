
import paramiko

VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASSWORD = "<REDACTED_PASSWORD>"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, port=22, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=10)

print("Checking git status on VPS...")
stdin, stdout, stderr = ssh.exec_command("cd /root/cryptomentor-bot && git status")
print(stdout.read().decode())

print("\nChecking last commit on VPS...")
stdin, stdout, stderr = ssh.exec_command("cd /root/cryptomentor-bot && git log -1 --oneline")
print(stdout.read().decode())

ssh.close()
