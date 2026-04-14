import paramiko

def check_nginx_top():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('147.93.156.165', username='root', password='rMM2m63P', timeout=10)
        
        commands = [
            "echo '--- nginx-www.conf top ---'",
            "head -n 20 /root/cryptomentor-bot/website-backend/nginx-www.conf"
        ]
        
        full_cmd = " && ".join(commands)
        stdin, stdout, stderr = ssh.exec_command(full_cmd)
        print(stdout.read().decode('utf-8'))
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_nginx_top()
