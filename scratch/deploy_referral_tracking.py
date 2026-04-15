#!/usr/bin/env python3
import os
import paramiko

VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASS = "<REDACTED_VPS_PASSWORD>"
VPS_BASE = "/root/cryptomentor-bot"

def main():
    print(f"Deploying referral tracking update to {VPS_HOST}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=20)
    sftp = ssh.open_sftp()

    # 1. Sync backend file
    backend_local = "website-backend/app/routes/user.py"
    backend_remote = f"{VPS_BASE}/{backend_local}"
    print(f"Uploading backend: {backend_local}...")
    sftp.put(backend_local, backend_remote)

    # 2. Sync frontend dist
    dist_local = "website-frontend/dist"
    dist_remote = "/var/www/cryptomentor"
    print(f"Uploading frontend dist from {dist_local}...")
    
    # Create remote dist dir if missing
    try:
        ssh.exec_command(f"mkdir -p {dist_remote}")
    except:
        pass

    for root, dirs, files in os.walk(dist_local):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, dist_local)
            remote_path = f"{dist_remote}/{rel_path}".replace("\\", "/")
            
            # Ensure subdir exists
            remote_subdir = os.path.dirname(remote_path)
            ssh.exec_command(f"mkdir -p {remote_subdir}")
            
            sftp.put(local_path, remote_path)
            print(f"  * {rel_path}")

    # 3. Restart Services
    print("\nRestarting services...")
    ssh.exec_command("sudo systemctl restart cryptomentor-web")
    ssh.exec_command("sudo systemctl reload nginx")
    
    print("Deployment complete!")
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    main()
