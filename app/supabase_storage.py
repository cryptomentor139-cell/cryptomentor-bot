"""
Supabase Storage Integration for Railway Deployment
Fallback storage when G: drive not available
"""
import os
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SupabaseStorage:
    """Upload signal logs to Supabase Storage"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.bucket_name = "cryptobot-signals"
        self._init_storage()
    
    def _init_storage(self):
        """Initialize Supabase Storage"""
        try:
            # Check if we should use Supabase
            use_supabase = os.getenv('USE_SUPABASE_STORAGE', 'false').lower() == 'true'
            
            if not use_supabase:
                logger.info("Supabase Storage disabled (USE_SUPABASE_STORAGE=false)")
                return
            
            from supabase import create_client
            
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
            
            if not url or not key:
                logger.warning("Supabase credentials not found")
                return
            
            self.client = create_client(url, key)
            self.enabled = True
            logger.info("✅ Supabase Storage initialized")
            
            # Ensure bucket exists
            self._ensure_bucket()
            
        except ImportError:
            logger.warning("Supabase package not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase Storage: {e}")
    
    def _ensure_bucket(self):
        """Ensure bucket exists"""
        try:
            # Try to get bucket
            buckets = self.client.storage.list_buckets()
            bucket_exists = any(b['name'] == self.bucket_name for b in buckets)
            
            if not bucket_exists:
                # Create bucket
                self.client.storage.create_bucket(
                    self.bucket_name,
                    options={"public": False}
                )
                logger.info(f"✅ Created bucket: {self.bucket_name}")
            else:
                logger.info(f"✅ Bucket exists: {self.bucket_name}")
                
        except Exception as e:
            logger.warning(f"Bucket check failed: {e}")
    
    def upload_file(self, local_path: Path, remote_path: str = None):
        """Upload file to Supabase Storage"""
        if not self.enabled:
            return False
        
        try:
            if not local_path.exists():
                logger.warning(f"File not found: {local_path}")
                return False
            
            # Use filename as remote path if not specified
            if remote_path is None:
                remote_path = local_path.name
            
            # Read file content
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Supabase
            self.client.storage.from_(self.bucket_name).upload(
                remote_path,
                file_content,
                file_options={"upsert": "true"}
            )
            
            logger.info(f"✅ Uploaded: {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Upload failed for {local_path}: {e}")
            return False
    
    def upload_all_logs(self):
        """Upload all log files to Supabase"""
        if not self.enabled:
            logger.warning("Supabase Storage not enabled")
            return 0, 0
        
        try:
            log_dir = Path("signal_logs")
            if not log_dir.exists():
                logger.warning("signal_logs directory not found")
                return 0, 0
            
            uploaded = 0
            failed = 0
            
            # Upload all .jsonl files
            for file in log_dir.glob("*.jsonl"):
                if self.upload_file(file):
                    uploaded += 1
                else:
                    failed += 1
            
            logger.info(f"📊 Upload complete: {uploaded} files uploaded, {failed} failed")
            return uploaded, failed
            
        except Exception as e:
            logger.error(f"Upload all failed: {e}")
            return 0, 0
    
    def download_file(self, remote_path: str, local_path: Path):
        """Download file from Supabase Storage"""
        if not self.enabled:
            return False
        
        try:
            # Download from Supabase
            response = self.client.storage.from_(self.bucket_name).download(remote_path)
            
            # Save to local file
            local_path.parent.mkdir(exist_ok=True, parents=True)
            with open(local_path, 'wb') as f:
                f.write(response)
            
            logger.info(f"✅ Downloaded: {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed for {remote_path}: {e}")
            return False
    
    def list_files(self, prefix: str = ""):
        """List files in Supabase Storage"""
        if not self.enabled:
            return []
        
        try:
            files = self.client.storage.from_(self.bucket_name).list(prefix)
            return [f['name'] for f in files]
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []
    
    def get_status(self):
        """Get storage status"""
        if not self.enabled:
            return {
                "enabled": False,
                "message": "Supabase Storage not configured"
            }
        
        try:
            # Count files
            files = self.list_files()
            
            return {
                "enabled": True,
                "bucket": self.bucket_name,
                "files_count": len(files),
                "status": "connected"
            }
        except Exception as e:
            return {
                "enabled": True,
                "bucket": self.bucket_name,
                "status": "error",
                "error": str(e)
            }

# Global instance
supabase_storage = SupabaseStorage()
