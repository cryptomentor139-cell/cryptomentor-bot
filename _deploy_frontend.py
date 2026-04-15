#!/usr/bin/env python3
"""Deploy built frontend to VPS targets using environment-based credentials."""
import paramiko
import os

HOST = os.getenv("CRYPTOMENTOR_VPS_HOST", "")
USER = os.getenv("CRYPTOMENTOR_VPS_USER", "root")
PASS = os.getenv("CRYPTOMENTOR_VPS_PASSWORD", "")
LOCAL_DIST = "website-frontend/dist"

TARGETS = [
    "/var/www/cryptomentor",
    "/root/cryptomentor-bot/website-frontend/dist",
]

def upload_dir(sftp, local_dir, remote_dir):
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
    for entry in os.listdir(local_dir):
        local_path = os.path.join(local_dir, entry)
        remote_path = remote_dir + "/" + entry
        if os.path.isdir(local_path):
            upload_dir(sftp, local_path, remote_path)
        else:
            sftp.put(local_path, remote_path)

def run(ssh, cmd):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    return stdout.read().decode("utf-8", errors="replace") + stderr.read().decode("utf-8", errors="replace")

def main():
    if not HOST or not PASS:
        raise RuntimeError(
            "Missing VPS credentials. Set CRYPTOMENTOR_VPS_HOST and CRYPTOMENTOR_VPS_PASSWORD."
        )
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)
    sftp = ssh.open_sftp()

    for target in TARGETS:
        print(f"\nDeploying to {target} ...")
        # Remove all old assets
        run(ssh, f"rm -rf {target}/assets")
        # Upload new build
        upload_dir(sftp, LOCAL_DIST, target)
        # Verify index.html
        out = run(ssh, f"cat {target}/index.html")
        print(f"  index.html: {out.strip()}")

    sftp.close()

    # Also update the sites-available/cryptomentor.id root path to /var/www/cryptomentor
    # so they stay in sync after git pulls
    print("\nUpdating sites-available/cryptomentor.id root path...")
    run(ssh, "sed -i 's|root /root/cryptomentor-bot/website-frontend/dist;|root /var/www/cryptomentor;|g' /etc/nginx/sites-available/cryptomentor.id")
    print(run(ssh, "grep 'root ' /etc/nginx/sites-available/cryptomentor.id"))

    # Reload nginx
    print("Reloading nginx...")
    print(run(ssh, "nginx -t && nginx -s reload && echo 'nginx reloaded'"))

    # Final check
    print("=== Final: live index.html ===")
    print(run(ssh, "curl -s https://cryptomentor.id/ --max-time 8 2>&1"))

    ssh.close()
    print("Done.")

if __name__ == "__main__":
    main()
