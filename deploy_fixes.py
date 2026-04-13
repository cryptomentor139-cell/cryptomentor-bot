import paramiko
import os

files_to_upload = [
    ('Bismillah/app/sideways_detector.py', '/root/cryptomentor-bot/Bismillah/app/sideways_detector.py'),
    ('Bismillah/app/autosignal_async.py', '/root/cryptomentor-bot/Bismillah/app/autosignal_async.py'),
    ('Bismillah/app/micro_momentum_detector.py', '/root/cryptomentor-bot/Bismillah/app/micro_momentum_detector.py'),
    ('Bismillah/app/trading_mode.py', '/root/cryptomentor-bot/Bismillah/app/trading_mode.py'),
    ('Bismillah/app/bitunix_autotrade_client.py', '/root/cryptomentor-bot/Bismillah/app/bitunix_autotrade_client.py'),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P')

sftp = ssh.open_sftp()
for local, remote in files_to_upload:
    print(f"Uploading {local} to {remote}...")
    sftp.put(local, remote)
sftp.close()

print("Restarting cryptomentor.service...")
ssh.exec_command('systemctl restart cryptomentor.service')
print("Service restarted.")

ssh.close()
