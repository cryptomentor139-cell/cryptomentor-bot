"""
Local Google Drive Sync - Simplified version using mounted G: drive
No need for OAuth API - just direct file operations
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LocalGDriveSync:
    """Sync logs ke Google Drive yang sudah ter-mount di G:"""
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        self.gdrive_path = os.getenv('GDRIVE_PATH', 'G:/CryptoBot_Signals')
        self.local_path = Path("signal_logs")
        self.enabled = self._check_gdrive_available()
    
    def _check_gdrive_available(self):
        """Check apakah G: drive tersedia"""
        try:
            if os.path.exists('G:/'):
                logger.info("✅ Google Drive (G:) detected")
                # Buat folder jika belum ada
                gdrive_dir = Path(self.gdrive_path)
                if not gdrive_dir.exists():
                    gdrive_dir.mkdir(exist_ok=True, parents=True)
                return True
            else:
                logger.warning("⚠️ Google Drive (G:) not found - sync disabled")
                return False
        except Exception as e:
            logger.error(f"Failed to check G: drive: {e}")
            return False
    
    def sync_file(self, filename: str):
        """Sync single file ke G: drive"""
        if not self.enabled:
            return False
        
        try:
            source = self.local_path / filename
            dest = Path(self.gdrive_path) / filename
            
            if source.exists():
                shutil.copy2(source, dest)
                logger.info(f"✅ Synced: {filename}")
                return True
            else:
                logger.warning(f"⚠️ File not found: {filename}")
                return False
        except Exception as e:
            logger.error(f"❌ Sync failed for {filename}: {e}")
            return False
    
    def sync_all_logs(self):
        """Sync semua log files ke G: drive"""
        if not self.enabled:
            logger.warning("Sync disabled - G: drive not available")
            return
        
        try:
            synced = 0
            failed = 0
            
            # Sync semua file .jsonl
            for file in self.local_path.glob("*.jsonl"):
                if self.sync_file(file.name):
                    synced += 1
                else:
                    failed += 1
            
            logger.info(f"📊 Sync complete: {synced} files synced, {failed} failed")
            return synced, failed
            
        except Exception as e:
            logger.error(f"❌ Sync all failed: {e}")
            return 0, 0
    
    def get_sync_status(self):
        """Get status sync"""
        if not self.enabled:
            return {
                "enabled": False,
                "gdrive_path": self.gdrive_path,
                "message": "G: drive not available"
            }
        
        # Count files
        local_files = len(list(self.local_path.glob("*.jsonl")))
        gdrive_files = len(list(Path(self.gdrive_path).glob("*.jsonl"))) if self.enabled else 0
        
        return {
            "enabled": True,
            "gdrive_path": self.gdrive_path,
            "local_files": local_files,
            "gdrive_files": gdrive_files,
            "in_sync": local_files == gdrive_files
        }

# Global instance
local_gdrive_sync = LocalGDriveSync()
