
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

print("Checking nginx config...")
out, err = run_ssh("cat /etc/nginx/sites-available/www-cryptomentor.conf || cat /etc/nginx/sites-enabled/default")
print(out)

print("\nChecking directories in /root/cryptomentor-bot/...")
out, err = run_ssh("ls -F /root/cryptomentor-bot/")
print(out)

print("\nChecking for alternate frontend directories...")
out, err = run_ssh("find /root/cryptomentor-bot -maxdepth 3 -name 'dist*' -type d")
print(out)
