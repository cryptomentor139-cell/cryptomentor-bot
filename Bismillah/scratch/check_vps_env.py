import paramiko

def check_vps_env():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('147.93.156.165', username='root', password='rMM2m63P', timeout=10)
        
        commands = [
            "echo '--- web .env ---'",
            "cat /root/cryptomentor-bot/website-backend/.env | grep -E 'TELEGRAM|ADMIN'"
        ]
        
        full_cmd = " && ".join(commands)
        stdin, stdout, stderr = ssh.exec_command(full_cmd)
        print(stdout.read().decode('utf-8'))
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_vps_env()
