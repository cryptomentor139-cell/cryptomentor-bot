
import paramiko

VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASSWORD = "<REDACTED_PASSWORD>"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, port=22, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=10)

def safe_print(data):
    if isinstance(data, bytes):
        data = data.decode('utf-8', errors='replace')
    print(data.replace('\u25cf', '*').encode('ascii', 'replace').decode('ascii'))

print("Searching for any 'Starting' or 'scheduler' logs in last 500 lines...")
stdin, stdout, stderr = ssh.exec_command("journalctl -u cryptomentor.service -n 500 --no-pager | grep -E 'Starting|scheduler' | tail -n 50")
safe_print(stdout.read())

ssh.close()
