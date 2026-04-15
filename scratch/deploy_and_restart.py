
import paramiko
import time

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

print("--- Starting Redeploy/Restart Process ---")

# Step 1: Pull code
run_cmd("cd /root/cryptomentor-bot && git fetch ajax && git checkout main && git pull ajax main")

# Step 2: Restart services
services = ["cryptomentor.service", "cryptomentor-analytics.service", "cryptomentor-web.service"]
for svc in services:
    print(f"Restarting {svc}...")
    exit_code = run_cmd(f"systemctl restart {svc}")
    if exit_code == 0:
         print(f"SUCCESS: {svc} restarted.")
    else:
         print(f"FAILURE: {svc} restart failed (exit code {exit_code}).")

# Step 3: Verify bot status
print("\nVerifying bot service status...")
run_cmd("systemctl status cryptomentor.service --no-pager | head -n 10")

print("\n--- Deployment Complete ---")
ssh.close()
