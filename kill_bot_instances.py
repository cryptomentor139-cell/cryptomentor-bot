
#!/usr/bin/env python3
"""Kill conflicting bot instances"""

import os
import sys
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available - limited functionality")

def kill_bot_instances():
    """Kill existing bot instances"""
    print("🛑 CryptoMentor AI - Kill Bot Instances")
    print("=" * 40)
    
    if not PSUTIL_AVAILABLE:
        print("❌ psutil not installed. Installing...")
        try:
            os.system("pip install psutil")
            import psutil
            print("✅ psutil installed successfully")
        except Exception as e:
            print(f"❌ Failed to install psutil: {e}")
            return False
    
    killed_count = 0
    current_pid = os.getpid()
    
    try:
        print(f"🔍 Scanning for bot processes (excluding PID {current_pid})...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                    
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Look for bot-related processes
                if any(keyword in cmdline.lower() for keyword in ['main.py', 'bot.py', 'cryptomentor']):
                    print(f"🎯 Found bot process: PID {proc.info['pid']} - {cmdline[:50]}...")
                    
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                        print(f"✅ Terminated PID {proc.info['pid']}")
                        killed_count += 1
                    except psutil.TimeoutExpired:
                        proc.kill()
                        print(f"🔪 Force killed PID {proc.info['pid']}")
                        killed_count += 1
                    except Exception as e:
                        print(f"❌ Failed to kill PID {proc.info['pid']}: {e}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    except Exception as e:
        print(f"❌ Error scanning processes: {e}")
        return False
    
    print(f"\n📊 Summary: {killed_count} bot instances terminated")
    
    if killed_count > 0:
        print("⏳ Waiting 5 seconds for cleanup...")
        time.sleep(5)
        print("✅ Cleanup completed")
    else:
        print("✅ No conflicting bot instances found")
    
    return True

if __name__ == "__main__":
    kill_bot_instances()
