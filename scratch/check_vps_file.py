
import paramiko

VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASSWORD = "<REDACTED_PASSWORD>"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, port=22, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=10)

print("Reading scheduler.py from VPS...")
stdin, stdout, stderr = ssh.exec_command("tail -n 30 /root/cryptomentor-bot/Bismillah/app/scheduler.py")
print(stdout.read().decode())

ssh.close()
