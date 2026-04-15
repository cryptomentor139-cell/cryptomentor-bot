
import paramiko

VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASSWORD = "<REDACTED_PASSWORD>"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, port=22, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=10)

print("Checking analytics service unit file...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/cryptomentor-analytics.service")
print(stdout.read().decode())

ssh.close()
