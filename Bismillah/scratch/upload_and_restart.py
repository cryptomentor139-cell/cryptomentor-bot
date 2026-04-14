import paramiko
import os

def upload_and_restart():
    host = '147.93.156.165'
    user = 'root'
    pw = 'rMM2m63P'
    
    files_to_upload = [
        ('scalping_engine.deploy.py', '/root/cryptomentor-bot/scalping_engine.deploy.py'),
        ('Bismillah/app/autotrade_engine.py', '/root/cryptomentor-bot/Bismillah/app/autotrade_engine.py'),
    ]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=pw, timeout=10)
        sftp = ssh.open_sftp()
        
        for local_path, remote_path in files_to_upload:
            print(f"Uploading {local_path} to {remote_path}...")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        
        print("Restarting services...")
        commands = [
            'systemctl restart cryptomentor.service',
            'systemctl restart cryptomentor-web.service'
        ]
        ssh.exec_command(" && ".join(commands))
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_and_restart()
