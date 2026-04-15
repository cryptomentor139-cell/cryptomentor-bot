#!/usr/bin/env python3
"""Diagnose and fix nginx/SSL for analytics4896.cryptomentor.id"""
import paramiko

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

def run(ssh, cmd, timeout=15):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)

    print("=== Nginx status ===")
    out, _ = run(ssh, "systemctl is-active nginx")
    print("nginx active:", out.strip())

    print("\n=== Nginx error log (last 20) ===")
    out, _ = run(ssh, "tail -20 /var/log/nginx/error.log 2>/dev/null || echo 'no error log'")
    print(out)

    print("=== SSL cert expiry ===")
    out, _ = run(ssh, "certbot certificates 2>&1 | grep -A5 'analytics4896'")
    print(out or "(not found)")

    print("\n=== nginx config for analytics4896 ===")
    out, _ = run(ssh, "cat /etc/nginx/sites-available/analytics4896.cryptomentor.id 2>/dev/null || echo 'file not found'")
    print(out)

    print("\n=== Port 443 listening? ===")
    out, _ = run(ssh, "ss -tlnp | grep 443")
    print(out or "(nothing on 443)")

    print("\n=== Port 80 listening? ===")
    out, _ = run(ssh, "ss -tlnp | grep ':80 '")
    print(out or "(nothing on 80)")

    print("\n=== Trying to start/restart nginx ===")
    out, err = run(ssh, "systemctl restart nginx 2>&1; systemctl is-active nginx")
    print(out, err)

    print("\n=== nginx config test ===")
    out, err = run(ssh, "nginx -t 2>&1")
    print(out, err)

    print("\n=== Re-test HTTPS after restart ===")
    out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' https://analytics4896.cryptomentor.id/health --max-time 10 2>&1")
    print(f"HTTPS health code: {out}")

    ssh.close()

if __name__ == "__main__":
    main()
