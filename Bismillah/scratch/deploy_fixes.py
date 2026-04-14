import paramiko
import os
import glob

def deploy():
    host = '147.93.156.165'
    user = 'root'
    pw = 'rMM2m63P'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=pw, timeout=10)
        sftp = ssh.open_sftp()
        
        # 1. Upload Backend Changes
        files_to_upload = [
            ('website-backend/app/routes/signals.py', '/root/cryptomentor-bot/website-backend/app/routes/signals.py'),
            ('scalping_engine.deploy.py', '/root/cryptomentor-bot/scalping_engine.deploy.py'),
            ('Bismillah/app/autotrade_engine.py', '/root/cryptomentor-bot/Bismillah/app/autotrade_engine.py'),
        ]
        
        for local_path, remote_path in files_to_upload:
            print(f"Uploading {local_path}...")
            sftp.put(local_path, remote_path)
        
        # 2. Upload Frontend Changes (dist folder)
        print("Cleaning remote assets...")
        ssh.exec_command('rm -rf /root/cryptomentor-bot/website-frontend/dist/assets/*')
        
        print("Uploading index.html...")
        sftp.put('website-frontend/dist/index.html', '/root/cryptomentor-bot/website-frontend/dist/index.html')
        
        local_assets_dir = 'website-frontend/dist/assets'
        remote_assets_dir = '/root/cryptomentor-bot/website-frontend/dist/assets'
        
        try:
            sftp.mkdir(remote_assets_dir)
        except IOError:
            pass
            
        for local_asset in glob.glob(os.path.join(local_assets_dir, '*')):
            filename = os.path.basename(local_asset)
            print(f"Uploading asset: {filename}...")
            sftp.put(local_asset, f"{remote_assets_dir}/{filename}")
            
        sftp.close()
        
        # 3. Restart Services
        print("Restarting services...")
        ssh.exec_command('systemctl restart cryptomentor.service')
        ssh.exec_command('systemctl restart cryptomentor-web.service')
        
        print("Deployment Complete!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
