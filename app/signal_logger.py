"""
Signal Logger - Menyimpan semua prompt user dan tracking winrate signal
Langsung save ke Google Drive (G:) jika tersedia
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SignalLogger:
    """Logger untuk tracking semua signal dan prompt user"""
    
    def __init__(self):
        # Load .env if not loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        # Cek apakah G: drive tersedia (Google Drive for Desktop)
        gdrive_path = os.getenv('GDRIVE_PATH', 'G:/CryptoBot_Signals')
        
        # Check if G: drive path exists
        if os.path.exists('G:/') and os.path.exists(os.path.dirname(gdrive_path)):
            # Gunakan G: drive jika tersedia
            self.log_dir = Path(gdrive_path)
            self.use_gdrive = True
            logger.info(f"✅ Using Google Drive: {self.log_dir}")
        else:
            # Fallback ke local jika G: tidak tersedia
            self.log_dir = Path("signal_logs")
            self.use_gdrive = False
            logger.info(f"⚠️ G: drive not found, using local: {self.log_dir}")
        
        # Create directory if not exists
        try:
            self.log_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            logger.warning(f"Failed to create {self.log_dir}, using local: {e}")
            self.log_dir = Path("signal_logs")
            self.use_gdrive = False
            self.log_dir.mkdir(exist_ok=True, parents=True)
        
    def log_user_prompt(self, user_id: int, username: str, command: str, symbol: str = None, timeframe: str = None):
        """Simpan prompt user ke file"""
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "username": username,
            "command": command,
            "symbol": symbol,
            "timeframe": timeframe
        }
        
        # Simpan ke file harian
        daily_file = self.log_dir / f"prompts_{date_str}.jsonl"
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        return log_entry
    
    def log_signal_result(self, user_id: int, symbol: str, timeframe: str, 
                         entry_price: float, tp1: float, tp2: float, sl: float,
                         signal_type: str = "LONG"):
        """Log signal yang diberikan untuk tracking winrate"""
        timestamp = datetime.now()
        
        signal_entry = {
            "signal_id": f"{user_id}_{symbol}_{int(timestamp.timestamp())}",
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "signal_type": signal_type,
            "entry_price": entry_price,
            "tp1": tp1,
            "tp2": tp2,
            "sl": sl,
            "status": "ACTIVE",
            "result": None,
            "pnl_percent": None,
            "closed_at": None
        }
        
        # Simpan ke file tracking
        signals_file = self.log_dir / "active_signals.jsonl"
        with open(signals_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(signal_entry, ensure_ascii=False) + "\n")
            
        return signal_entry["signal_id"]
    
    def update_signal_result(self, signal_id: str, result: str, pnl_percent: float):
        """Update hasil signal (WIN/LOSS)"""
        signals_file = self.log_dir / "active_signals.jsonl"
        completed_file = self.log_dir / "completed_signals.jsonl"
        
        if not signals_file.exists():
            return False
            
        # Baca semua signal
        signals = []
        with open(signals_file, "r", encoding="utf-8") as f:
            for line in f:
                signals.append(json.loads(line))
        
        # Update signal yang match
        updated = False
        for signal in signals:
            if signal["signal_id"] == signal_id:
                signal["status"] = "CLOSED"
                signal["result"] = result
                signal["pnl_percent"] = pnl_percent
                signal["closed_at"] = datetime.now().isoformat()
                updated = True
                
                # Pindahkan ke completed
                with open(completed_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(signal, ensure_ascii=False) + "\n")
                break
        
        if updated:
            # Tulis ulang active signals tanpa yang sudah closed
            with open(signals_file, "w", encoding="utf-8") as f:
                for signal in signals:
                    if signal["signal_id"] != signal_id:
                        f.write(json.dumps(signal, ensure_ascii=False) + "\n")
        
        return updated
    
    def calculate_winrate(self, days: int = 7):
        """Hitung winrate signal dalam periode tertentu"""
        completed_file = self.log_dir / "completed_signals.jsonl"
        
        if not completed_file.exists():
            return {
                "total_signals": 0,
                "wins": 0,
                "losses": 0,
                "winrate": 0,
                "avg_pnl": 0
            }
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        wins = 0
        losses = 0
        total_pnl = 0
        
        with open(completed_file, "r", encoding="utf-8") as f:
            for line in f:
                signal = json.loads(line)
                signal_date = datetime.fromisoformat(signal["closed_at"])
                
                if signal_date >= cutoff_date:
                    if signal["result"] == "WIN":
                        wins += 1
                    elif signal["result"] == "LOSS":
                        losses += 1
                    
                    if signal["pnl_percent"]:
                        total_pnl += signal["pnl_percent"]
        
        total = wins + losses
        winrate = (wins / total * 100) if total > 0 else 0
        avg_pnl = (total_pnl / total) if total > 0 else 0
        
        return {
            "total_signals": total,
            "wins": wins,
            "losses": losses,
            "winrate": round(winrate, 2),
            "avg_pnl": round(avg_pnl, 2)
        }
    
    def get_weekly_stats(self):
        """Dapatkan statistik mingguan untuk laporan"""
        stats = self.calculate_winrate(days=7)
        
        # Hitung total prompts
        prompts_count = 0
        week_ago = datetime.now() - timedelta(days=7)
        
        for file in self.log_dir.glob("prompts_*.jsonl"):
            try:
                date_str = file.stem.replace("prompts_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date >= week_ago:
                    with open(file, "r", encoding="utf-8") as f:
                        prompts_count += sum(1 for _ in f)
            except:
                continue
        
        stats["total_prompts"] = prompts_count
        return stats

# Global instance
signal_logger = SignalLogger()
