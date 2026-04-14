import paramiko
import os

def deploy():
    host = '147.93.156.165'
    user = 'root'
    pw = 'rMM2m63P'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        ssh.connect(host, username=user, password=pw, timeout=10)
        sftp = ssh.open_sftp()
        
        # 1. Upload Backend Changes
        files_to_upload = [
            ('Bismillah/app/bitunix_autotrade_client.py', '/root/cryptomentor-bot/Bismillah/app/bitunix_autotrade_client.py'),
            ('Bismillah/app/bingx_autotrade_client.py', '/root/cryptomentor-bot/Bismillah/app/bingx_autotrade_client.py'),
        ]
        
        for local_path, remote_path in files_to_upload:
            print(f"Uploading {local_path}...")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        
        # 2. Restart Services
        print("Restarting cryptomentor.service...")
        ssh.exec_command('systemctl restart cryptomentor.service')
        
        print("Restarting cryptomentor-web.service...")
        ssh.exec_command('systemctl restart cryptomentor-web.service')
        
        print("Deployment Complete!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
