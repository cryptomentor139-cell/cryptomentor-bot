"""
Script untuk integrate signal tracking ke bot
Run this after setting up Google Drive credentials
"""
import sys
from pathlib import Path

def integrate_tracking():
    """Add tracking integration to bot.py"""
    
    print("🔧 Integrating Signal Tracking System...")
    
    # 1. Check if signal_logs directory exists
    log_dir = Path("signal_logs")
    if not log_dir.exists():
        log_dir.mkdir()
        print("✅ Created signal_logs directory")
    
    # 2. Add .gitignore entries
    gitignore = Path(".gitignore")
    entries = [
        "gdrive_credentials.json",
        "gdrive_token.json",
        "signal_logs/",
    ]
    
    if gitignore.exists():
        with open(gitignore, "a") as f:
            f.write("\n# Signal Tracking\n")
            for entry in entries:
                f.write(f"{entry}\n")
        print("✅ Updated .gitignore")
    
    print("\n📋 Next Steps:")
    print("1. Setup Google Drive credentials (see SIGNAL_TRACKING_SETUP.md)")
    print("2. Add tracking calls to command handlers")
    print("3. Register new admin commands in bot.py")
    print("4. Start scheduler in bot main()")
    
    print("\n✅ Integration complete!")

if __name__ == "__main__":
    integrate_tracking()
