
#!/usr/bin/env python3
"""
System Health Monitor for CryptoMentor AI
Consolidates all health check and verification functionality
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from database import Database
from crypto_api import CryptoAPI

load_dotenv()

class SystemHealth:
    def __init__(self):
        self.db = Database()
        self.crypto_api = CryptoAPI()

    def check_environment(self):
        """Check deployment environment"""
        is_deployment = (
            os.getenv('REPLIT_DEPLOYMENT') == '1' or 
            os.getenv('REPL_DEPLOYMENT') == '1' or
            os.path.exists('/tmp/repl_deployment_flag')
        )
        return is_deployment

    def check_api_keys(self):
        """Check all API keys"""
        keys = {
            'telegram': bool(os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN')),
            'coinapi': bool(os.getenv('COINAPI_API_KEY') or os.getenv('COINAPI_KEY')),
            'cmc': bool(os.getenv('CMC_API_KEY') or os.getenv('COINMARKETCAP_API_KEY')),
            'supabase_url': bool(os.getenv('SUPABASE_URL')),
            'supabase_key': bool(os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')),
            'openai': bool(os.getenv('OPENAI_API_KEY')),
            'cryptonews': bool(os.getenv('CRYPTONEWS_API_KEY'))
        }
        return keys

    def check_database_health(self):
        """Check database health"""
        try:
            stats = self.db.get_bot_statistics()
            
            # Check for data issues
            self.db.cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NULL")
            null_ids = self.db.cursor.fetchone()[0]
            
            self.db.cursor.execute("SELECT COUNT(*) FROM users WHERE credits < 0")
            negative_credits = self.db.cursor.fetchone()[0]
            
            return {
                'total_users': stats['total_users'],
                'premium_users': stats['premium_users'],
                'data_issues': null_ids + negative_credits,
                'healthy': null_ids == 0 and negative_credits == 0
            }
        except Exception as e:
            return {'error': str(e), 'healthy': False}

    def check_api_connectivity(self):
        """Check API connectivity"""
        apis = {}
        
        # Binance
        try:
            response = requests.get("https://api.binance.com/api/v3/ping", timeout=10)
            apis['binance'] = response.status_code == 200
        except:
            apis['binance'] = False
        
        # CoinAPI (if key exists)
        coinapi_key = os.getenv('COINAPI_API_KEY') or os.getenv('COINAPI_KEY')
        if coinapi_key:
            try:
                response = requests.get(
                    "https://rest.coinapi.io/v1/exchangerate/BTC/USD",
                    headers={'X-CoinAPI-Key': coinapi_key},
                    timeout=10
                )
                apis['coinapi'] = response.status_code == 200
            except:
                apis['coinapi'] = False
        else:
            apis['coinapi'] = None
        
        # CoinMarketCap (if key exists)
        cmc_key = os.getenv('CMC_API_KEY') or os.getenv('COINMARKETCAP_API_KEY')
        if cmc_key:
            try:
                response = requests.get(
                    "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
                    params={'symbol': 'BTC'},
                    headers={'X-CMC_PRO_API_KEY': cmc_key},
                    timeout=10
                )
                apis['coinmarketcap'] = response.status_code == 200
            except:
                apis['coinmarketcap'] = False
        else:
            apis['coinmarketcap'] = None
        
        # Supabase (if configured)
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        if supabase_url and supabase_key:
            try:
                response = requests.get(
                    f"{supabase_url}/rest/v1/",
                    headers={
                        'apikey': supabase_key,
                        'Authorization': f'Bearer {supabase_key}'
                    },
                    timeout=10
                )
                apis['supabase'] = response.status_code in [200, 404]  # 404 is also valid for base endpoint
            except:
                apis['supabase'] = False
        else:
            apis['supabase'] = None
        
        # OpenAI (if key exists)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={'Authorization': f'Bearer {openai_key}'},
                    timeout=10
                )
                apis['openai'] = response.status_code == 200
            except:
                apis['openai'] = False
        else:
            apis['openai'] = None
        
        # CryptoNews (if key exists)
        cryptonews_key = os.getenv('CRYPTONEWS_API_KEY')
        if cryptonews_key:
            try:
                response = requests.get(
                    "https://cryptonews-api.com/api/v1/category",
                    params={'section': 'general', 'items': 1, 'token': cryptonews_key},
                    timeout=10
                )
                apis['cryptonews'] = response.status_code == 200
            except:
                apis['cryptonews'] = False
        else:
            apis['cryptonews'] = None
        
        return apis

    def generate_health_report(self):
        """Generate comprehensive health report"""
        print("🏥 CryptoMentor AI - System Health Report")
        print("=" * 50)
        print(f"⏰ Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Environment
        is_deployment = self.check_environment()
        print(f"🌍 Environment: {'🚀 DEPLOYMENT' if is_deployment else '🔧 DEVELOPMENT'}")
        
        # API Keys
        keys = self.check_api_keys()
        print(f"\n🔐 API Keys Configuration:")
        print(f"  • TELEGRAM: {'✅ SET' if keys['telegram'] else '❌ MISSING'}")
        print(f"  • COINAPI_API_KEY: {'✅ SET' if keys['coinapi'] else '❌ MISSING'}")
        print(f"  • CMC_API_KEY: {'✅ SET' if keys['cmc'] else '❌ MISSING'}")
        print(f"  • SUPABASE_URL: {'✅ SET' if keys['supabase_url'] else '❌ MISSING'}")
        print(f"  • SUPABASE_KEY: {'✅ SET' if keys['supabase_key'] else '❌ MISSING'}")
        print(f"  • OPENAI_API_KEY: {'✅ SET' if keys['openai'] else '❌ MISSING'}")
        print(f"  • CRYPTONEWS_API_KEY: {'✅ SET' if keys['cryptonews'] else '❌ MISSING'}")
        
        # Database
        db_health = self.check_database_health()
        print(f"\n🗄️ Database:")
        if 'error' not in db_health:
            print(f"  • Users: {db_health['total_users']} (Premium: {db_health['premium_users']})")
            print(f"  • Health: {'✅ GOOD' if db_health['healthy'] else '⚠️ ISSUES'}")
            if db_health['data_issues'] > 0:
                print(f"  • Issues: {db_health['data_issues']} records need fixing")
        else:
            print(f"  • Error: {db_health['error']}")
        
        # API Connectivity
        apis = self.check_api_connectivity()
        print(f"\n🌐 API Connectivity Status:")
        print(f"  • BINANCE: {'✅ ONLINE' if apis.get('binance') else '❌ OFFLINE'}")
        
        coinapi_status = apis.get('coinapi')
        if coinapi_status is None:
            print(f"  • COINAPI: ⚠️ NOT CONFIGURED")
        else:
            print(f"  • COINAPI: {'✅ ONLINE' if coinapi_status else '❌ OFFLINE'}")
        
        cmc_status = apis.get('coinmarketcap')
        if cmc_status is None:
            print(f"  • COINMARKETCAP: ⚠️ NOT CONFIGURED")
        else:
            print(f"  • COINMARKETCAP: {'✅ ONLINE' if cmc_status else '❌ OFFLINE'}")
        
        supabase_status = apis.get('supabase')
        if supabase_status is None:
            print(f"  • SUPABASE: ⚠️ NOT CONFIGURED")
        else:
            print(f"  • SUPABASE: {'✅ ONLINE' if supabase_status else '❌ OFFLINE'}")
        
        openai_status = apis.get('openai')
        if openai_status is None:
            print(f"  • OPENAI: ⚠️ NOT CONFIGURED")
        else:
            print(f"  • OPENAI: {'✅ ONLINE' if openai_status else '❌ OFFLINE'}")
        
        cryptonews_status = apis.get('cryptonews')
        if cryptonews_status is None:
            print(f"  • CRYPTONEWS: ⚠️ NOT CONFIGURED")
        else:
            print(f"  • CRYPTONEWS: {'✅ ONLINE' if cryptonews_status else '❌ OFFLINE'}")
        
        # Overall Status
        working_keys = sum(keys.values())
        working_apis = sum(1 for v in apis.values() if v is True)
        
        if working_keys >= 2 and working_apis >= 1 and db_health.get('healthy', False):
            status = "🟢 EXCELLENT"
        elif working_keys >= 1 and working_apis >= 1:
            status = "🟡 GOOD"
        else:
            status = "🔴 NEEDS ATTENTION"
        
        print(f"\n🎯 Overall Status: {status}")
        
        return {
            'environment': is_deployment,
            'keys': keys,
            'database': db_health,
            'apis': apis,
            'overall_healthy': working_keys >= 2 and working_apis >= 1
        }

def main():
    """Main health check function"""
    health = SystemHealth()
    report = health.generate_health_report()
    return report['overall_healthy']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
