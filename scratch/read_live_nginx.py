
import paramiko

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

def run_ssh(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    ssh.close()
    return out, err

print("Content of /etc/nginx/sites-available/cryptomentor.id:")
out, err = run_ssh("cat /etc/nginx/sites-available/cryptomentor.id")
print(out)
