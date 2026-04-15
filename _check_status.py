#!/usr/bin/env python3
import paramiko

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

def run(ssh, cmd):
    _, stdout, _ = ssh.exec_command(cmd, timeout=15)
    return stdout.read().decode("utf-8", errors="replace")

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)

    print("=== VPS git stash list ===")
    print(run(ssh, "cd /root/cryptomentor-bot && git stash list 2>&1"))

    print("=== VPS git status ===")
    print(run(ssh, "cd /root/cryptomentor-bot && git status --short 2>&1"))

    print("=== VPS git log (last 5) ===")
    print(run(ssh, "cd /root/cryptomentor-bot && git log --oneline -5 2>&1"))

    print("=== VPS App.jsx diff vs HEAD ===")
    print(run(ssh, "cd /root/cryptomentor-bot && git diff HEAD -- website-frontend/src/App.jsx 2>&1 | head -100"))

    print("=== Is original CXZ1mQcu.js still anywhere on VPS? ===")
    print(run(ssh, "find / -name 'index-CXZ1mQcu.js' 2>/dev/null"))

    print("=== VPS App.jsx last modified ===")
    print(run(ssh, "ls -la /root/cryptomentor-bot/website-frontend/src/App.jsx"))

    print("=== VPS App.jsx size vs local ===")
    print(run(ssh, "wc -c /root/cryptomentor-bot/website-frontend/src/App.jsx"))

    ssh.close()

if __name__ == "__main__":
    main()
