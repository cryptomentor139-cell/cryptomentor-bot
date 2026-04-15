#!/usr/bin/env python3
"""Deploy updated analytics files to VPS."""
import paramiko

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

FILES = [
    ("Bismillah/analytics_api.py", "/root/cryptomentor-bot/Bismillah/analytics_api.py"),
    ("Bismillah/analytics_dashboard.html", "/root/cryptomentor-bot/Bismillah/analytics_dashboard.html"),
]

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)
    sftp = ssh.open_sftp()

    for local, remote in FILES:
        with open(local, "rb") as f:
            data = f.read()
        with sftp.file(remote, "wb") as f:
            f.write(data)
        print(f"Uploaded: {local} -> {remote}")

    sftp.close()

    # Restart service
    print("\nRestarting service...")
    _, stdout, stderr = ssh.exec_command("systemctl restart cryptomentor-analytics && sleep 2 && systemctl is-active cryptomentor-analytics")
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f"Status: {out}")
    if err:
        print(f"Stderr: {err}")

    # Quick sanity check
    print("\nSanity check...")
    _, stdout, _ = ssh.exec_command("curl -s http://localhost:8896/health")
    print("Health:", stdout.read().decode("utf-8", errors="replace").strip())

    _, stdout, _ = ssh.exec_command(
        "curl -s -X POST http://localhost:8896/auth/login "
        "-H 'Content-Type: application/json' "
        "-d '{\"password\": \"secret4896\"}' | python3 -c \"import json,sys; d=json.load(sys.stdin); print('Login OK, token len:', len(d.get('token','')))\""
    )
    print(stdout.read().decode("utf-8", errors="replace").strip())

    ssh.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
