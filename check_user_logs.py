import paramiko

def check_logs(user_id):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('147.93.156.165', port=22, username='root', password='rMM2m63P', timeout=10)
        
        # Check logs for user_id and ethusdt
        # We look for "Order placement failed"
        cmd = f"journalctl -u cryptomentor.service -n 5000 --no-pager | grep -a '{user_id}' | grep -a 'Order placement failed' -A 2"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        
        if not output:
             # Try searching specifically for the ETHUSDT failure
             cmd = f"journalctl -u cryptomentor.service -n 5000 --no-pager | grep -a '{user_id}' | grep -a 'ETHUSDT' -A 2"
             stdin, stdout, stderr = ssh.exec_command(cmd)
             output = stdout.read().decode('utf-8', errors='ignore')
             
        print("--- VPS LOGS ---")
        print(output)
        
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_logs(7675185179)
