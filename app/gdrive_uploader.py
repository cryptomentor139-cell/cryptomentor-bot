"""
Google Drive Uploader - Upload signal logs ke Google Drive
"""
import os
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GDriveUploader:
    """Upload logs ke Google Drive menggunakan PyDrive2"""
    
    def __init__(self):
        self.enabled = False
        self.drive = None
        self._init_drive()
    
    def _init_drive(self):
        """Initialize Google Drive connection"""
        try:
            from pydrive2.auth import GoogleAuth
            from pydrive2.drive import GoogleDrive
            
            # Check if credentials exist
            creds_file = Path("gdrive_credentials.json")
            if not creds_file.exists():
                logger.warning("Google Drive credentials not found. Upload disabled.")
                return
            
            gauth = GoogleAuth()
            
            # Try to load saved credentials
            gauth.LoadCredentialsFile("gdrive_token.json")
            
            if gauth.credentials is None:
                # Authenticate if they're not there
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                # Refresh them if expired
                gauth.Refresh()
            else:
                # Initialize the saved creds
                gauth.Authorize()
            
            # Save the current credentials to a file
            gauth.SaveCredentialsFile("gdrive_token.json")
            
            self.drive = GoogleDrive(gauth)
            self.enabled = True
            logger.info("✅ Google Drive initialized successfully")
            
        except ImportError:
            logger.warning("PyDrive2 not installed. Run: pip install PyDrive2")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive: {e}")
    
    def upload_file(self, file_path: Path, folder_name: str = "CryptoBot_Signals"):
        """Upload file ke Google Drive"""
        if not self.enabled:
            logger.warning("Google Drive upload disabled")
            return None
        
        try:
            # Cari atau buat folder
            folder_id = self._get_or_create_folder(folder_name)
            
            # Upload file
            file_drive = self.drive.CreateFile({
                'title': file_path.name,
                'parents': [{'id': folder_id}]
            })
            file_drive.SetContentFile(str(file_path))
            file_drive.Upload()
            
            logger.info(f"✅ Uploaded {file_path.name} to Google Drive")
            return file_drive['id']
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path.name}: {e}")
            return None
    
    def _get_or_create_folder(self, folder_name: str):
        """Cari atau buat folder di Google Drive"""
        # Cari folder yang sudah ada
        file_list = self.drive.ListFile({
            'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        }).GetList()
        
        if file_list:
            return file_list[0]['id']
        
        # Buat folder baru
        folder = self.drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()
        return folder['id']
    
    def upload_daily_logs(self):
        """Upload semua log hari ini ke Google Drive"""
        if not self.enabled:
            return
        
        log_dir = Path("signal_logs")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Upload prompt logs
        prompt_file = log_dir / f"prompts_{today}.jsonl"
        if prompt_file.exists():
            self.upload_file(prompt_file)
        
        # Upload signal logs
        signals_file = log_dir / "active_signals.jsonl"
        if signals_file.exists():
            self.upload_file(signals_file)
        
        completed_file = log_dir / "completed_signals.jsonl"
        if completed_file.exists():
            self.upload_file(completed_file)

# Global instance
gdrive_uploader = GDriveUploader()
