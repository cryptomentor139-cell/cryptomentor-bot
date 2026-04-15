
import paramiko

VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASSWORD = "<REDACTED_PASSWORD>"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, port=22, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=10)

def run_cmd(cmd):
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    return stdout.channel.recv_exit_status()

print("--- Resetting Git on VPS to sync with Ajax ---")
run_cmd("cd /root/cryptomentor-bot && git stash")
run_cmd("cd /root/cryptomentor-bot && git fetch ajax && git reset --hard ajax/main")

print("\nRestarting services...")
services = ["cryptomentor.service", "cryptomentor-analytics.service", "cryptomentor-web.service"]
for svc in services:
    run_cmd(f"systemctl restart {svc}")

print("\nVerifying last commit now...")
run_cmd("cd /root/cryptomentor-bot && git log -1 --oneline")

ssh.close()
