
#!/usr/bin/env python3
import subprocess
import time
import os

def kill_all_bot_instances():
    """Kill all existing bot instances"""
    print("🛑 Killing all bot instances...")
    
    commands = [
        ["pkill", "-f", "main.py"],
        ["pkill", "-f", "bot.py"], 
        ["pkill", "-f", "telegram"],
        ["pkill", "-9", "-f", "python.*main.py"],
        ["killall", "-9", "python3"]
    ]
    
    killed = 0
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                killed += 1
                print(f"✅ Executed: {' '.join(cmd)}")
        except Exception as e:
            print(f"⚠️ Command failed: {' '.join(cmd)} - {e}")
    
    print(f"🔄 Cleanup completed, waiting 10 seconds...")
    time.sleep(10)
    print("✅ Ready to restart bot")

if __name__ == "__main__":
    kill_all_bot_instances()
