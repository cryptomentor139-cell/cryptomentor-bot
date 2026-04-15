
import os
import paramiko
from datetime import datetime

# ===== CONFIGURATION =====
VPS_HOST = "147.93.156.165"
VPS_USER = "root"
VPS_PASSWORD = "<REDACTED_PASSWORD>"
VPS_PORT = 22
VPS_BASE_DIR = "/root/cryptomentor-bot"

def master_deploy():
    """Deploy Frontend, Backend, and Nginx config"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {VPS_HOST}...")
        ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=<REDACTED_PASSWORD> timeout=15)
        sftp = ssh.open_sftp()
        print("Connected!")

        # 1. Deploy Frontend Bundle
        local_frontend = "website-frontend/dist"
        remote_frontend = f"{VPS_BASE_DIR}/website-frontend/dist"
        print(f"Deploying frontend to {remote_frontend}...")
        
        # Create remote dir
        ssh.exec_command(f"mkdir -p {remote_frontend}")
        
        for root, dirs, files in os.walk(local_frontend):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_frontend)
                remote_path = f"{remote_frontend}/{rel_path}".replace("\\", "/")
                
                remote_subdir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_subdir)
                except IOError:
                    ssh.exec_command(f"mkdir -p {remote_subdir}")
                
                sftp.put(local_path, remote_path)
        print("Frontend deployed.")

        # 2. Deploy Backend
        local_backend = "website-backend"
        remote_backend = f"{VPS_BASE_DIR}/website-backend"
        print(f"Deploying backend to {remote_backend}...")
        
        # We only upload .py, .txt, .conf, .example files to keep it clean
        for root, dirs, files in os.walk(local_backend):
            if "__pycache__" in root: continue
            for file in files:
                if not file.endswith(('.py', '.txt', '.conf', '.example', '.html')): continue
                
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_backend)
                remote_path = f"{remote_backend}/{rel_path}".replace("\\", "/")
                
                remote_subdir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_subdir)
                except IOError:
                    ssh.exec_command(f"mkdir -p {remote_subdir}")
                
                sftp.put(local_path, remote_path)
        print("Backend deployed.")

        # 3. Update Nginx Config
        local_nginx = "website-backend/nginx-www.conf"
        # The target file on VPS as identified by research
        remote_nginx_path = "/etc/nginx/sites-available/cryptomentor.id"
        
        print(f"Updating Nginx config at {remote_nginx_path}...")
        # Backup old first
        ssh.exec_command(f"cp {remote_nginx_path} {remote_nginx_path}.bak")
        
        # Upload new config
        sftp.put(local_nginx, "/tmp/nginx-www.conf")
        ssh.exec_command(f"cp /tmp/nginx-www.conf {remote_nginx_path}")
        
        # Ensure it's enabled (just in case)
        ssh.exec_command(f"ln -s {remote_nginx_path} /etc/nginx/sites-enabled/cryptomentor.id")
        
        # Test and Reload
        stdin, stdout, stderr = ssh.exec_command("nginx -t")
        err = stderr.read().decode()
        if "test is successful" in err:
            print("Nginx config test passed. Reloading...")
            ssh.exec_command("systemctl reload nginx")
            print("Nginx reloaded.")
        else:
            print("Nginx config test FAILED!")
            print(err)
            # Restore backup
            ssh.exec_command(f"cp {remote_nginx_path}.bak {remote_nginx_path}")
            ssh.exec_command("systemctl reload nginx")

        # 4. Restart Backend Service
        print("Restarting Backend service (cryptomentor-web)...")
        ssh.exec_command("systemctl restart cryptomentor-web")
        print("Backend service restarted.")

        sftp.close()
        ssh.close()
        print("\nMASTER DEPLOYMENT COMPLETE!")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    master_deploy()
