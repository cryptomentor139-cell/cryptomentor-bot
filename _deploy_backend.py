#!/usr/bin/env python3
"""Deploy updated backend files and restart services."""
import paramiko

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

BACKEND_FILES = [
    ("website-backend/app/routes/dashboard.py", "/root/cryptomentor-bot/website-backend/app/routes/dashboard.py"),
    ("website-backend/app/routes/engine.py", "/root/cryptomentor-bot/website-backend/app/routes/engine.py"),
    ("website-backend/app/routes/user.py", "/root/cryptomentor-bot/website-backend/app/routes/user.py"),
    ("Bismillah/app/autotrade_engine.py", "/root/cryptomentor-bot/Bismillah/app/autotrade_engine.py"),
    ("Bismillah/app/scalping_engine.py", "/root/cryptomentor-bot/Bismillah/app/scalping_engine.py"),
    ("Bismillah/app/trading_mode.py", "/root/cryptomentor-bot/Bismillah/app/trading_mode.py"),
]

def run(ssh, cmd, timeout=20):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)
    sftp = ssh.open_sftp()

    print("Uploading backend files...")
    for local, remote in BACKEND_FILES:
        try:
            with open(local, "rb") as f:
                data = f.read()
            with sftp.file(remote, "wb") as f:
                f.write(data)
            print(f"  OK: {local}")
        except Exception as e:
            print(f"  SKIP {local}: {e}")

    sftp.close()

    # Restart both web and bot
    print("\nRestarting cryptomentor-web...")
    out, _ = run(ssh, "systemctl restart cryptomentor-web && sleep 1 && systemctl is-active cryptomentor-web")
    print(f"  cryptomentor-web: {out.strip()}")

    print("Restarting cryptomentor bot...")
    out, _ = run(ssh, "systemctl restart cryptomentor && sleep 2 && systemctl is-active cryptomentor")
    print(f"  cryptomentor: {out.strip()}")

    ssh.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
