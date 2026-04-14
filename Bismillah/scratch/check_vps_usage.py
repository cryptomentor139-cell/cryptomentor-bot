import paramiko

def check_vps_status():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('147.93.156.165', username='root', password='rMM2m63P', timeout=10)
        
        commands = [
            "echo '--- Uptime & Load Average ---'",
            "uptime",
            "echo '\n--- CPU Info ---'",
            "lscpu | grep 'CPU(s):' | head -n 1",
            "top -bn1 | grep 'Cpu(s)'",
            "echo '\n--- Memory Info ---'",
            "free -h",
            "echo '\n--- Disk Info ---'",
            "df -h /",
            "echo '\n--- Top Processes (CPU Peak) ---'",
            "ps -eo pcpu,pmem,comm --sort=-pcpu | head -n 11"
        ]
        
        full_cmd = " && ".join(commands)
        stdin, stdout, stderr = ssh.exec_command(full_cmd)
        
        print(stdout.read().decode('utf-8'))
        err = stderr.read().decode('utf-8')
        if err:
            print("Errors:", err)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_vps_status()
