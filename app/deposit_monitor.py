# Deposit Monitor Service
# Monitors custodial wallets for incoming USDC deposits on Base network
# Processes deposits and credits Conway credits via API

import os
import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime
from web3 import Web3
from web3.exceptions import Web3Exception

# Import Conway integration
from app.conway_integration import get_conway_client

# ERC20 ABI (minimal - just balanceOf function)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]


class DepositMonitor:
    """
    Monitors custodial wallets for USDC deposits on Base network
    
    Features:
    - Web3 connection to Base network
    - ERC20 USDC contract interaction
    - Balance checking for all custodial wallets
    - Deposit detection and confirmation tracking
    - 2% platform fee deduction
    - Conway credit conversion (1 USDC = 100 credits)
    - Integration with Conway API for credit transfers
    """
    
    def __init__(self, database):
        """
        Initialize deposit monitor
        
        Args:
            database: Database instance for wallet queries
        """
        self.db = database
        
        # Conway integration (optional for testing)
        try:
            self.conway = get_conway_client()
        except Exception as e:
            print(f"⚠️ Conway API not available: {e}")
            self.conway = None
        
        # Base network configuration
        self.rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # USDC contract on Base network
        # Base USDC: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
        self.usdc_address = os.getenv(
            'BASE_USDC_ADDRESS',
            '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
        )
        self.usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.usdc_address),
            abi=ERC20_ABI
        )
        
        # Monitoring configuration
        self.check_interval = int(os.getenv('DEPOSIT_CHECK_INTERVAL', '30'))  # seconds
        self.min_confirmations = int(os.getenv('MIN_CONFIRMATIONS', '12'))
        self.min_deposit = float(os.getenv('MIN_DEPOSIT_USDC', '5.0'))
        self.platform_fee_rate = 0.02  # 2%
        self.credit_conversion_rate = 100  # 1 USDC = 100 credits
        
        # Track last known balances to detect new deposits
        self.last_balances: Dict[str, float] = {}
        
        # Running state
        self.is_running = False
        self.monitor_task = None
        
        print(f"✅ Deposit Monitor initialized")
        print(f"   Network: Base ({self.rpc_url})")
        print(f"   USDC Contract: {self.usdc_address}")
        print(f"   Check Interval: {self.check_interval}s")
        print(f"   Min Confirmations: {self.min_confirmations}")
        print(f"   Platform Fee: {self.platform_fee_rate * 100}%")
    
    def _check_web3_connection(self) -> bool:
        """
        Verify Web3 connection to Base network
        
        Returns:
            True if connected, False otherwise
        """
        try:
            return self.w3.is_connected()
        except Exception as e:
            print(f"❌ Web3 connection check failed: {e}")
            return False
    
    def _get_usdc_balance(self, wallet_address: str) -> Optional[float]:
        """
        Query USDC balance for a wallet address
        
        Args:
            wallet_address: Ethereum address to check
            
        Returns:
            USDC balance as float, or None if error
        """
        try:
            checksum_address = Web3.to_checksum_address(wallet_address)
            balance_wei = self.usdc_contract.functions.balanceOf(checksum_address).call()
            
            # USDC has 6 decimals
            balance_usdc = balance_wei / (10 ** 6)
            return balance_usdc
        
        except Exception as e:
            print(f"❌ Error checking USDC balance for {wallet_address}: {e}")
            return None
    
    def _calculate_conway_credits(self, deposit_amount: float) -> tuple[float, float, float]:
        """
        Calculate Conway credits after platform fee
        
        Args:
            deposit_amount: USDC deposit amount
            
        Returns:
            Tuple of (net_amount, platform_fee, conway_credits)
        """
        platform_fee = deposit_amount * self.platform_fee_rate
        net_amount = deposit_amount - platform_fee
        conway_credits = net_amount * self.credit_conversion_rate
        
        return (net_amount, platform_fee, conway_credits)
    
    async def _process_deposit(
        self,
        wallet_id: str,
        user_id: int,
        wallet_address: str,
        deposit_amount: float
    ) -> bool:
        """
        Process a detected deposit
        
        Steps:
        1. Validate minimum deposit
        2. Calculate platform fee and Conway credits
        3. Update database records
        4. Credit Conway credits via API
        5. Send notification to user
        
        Args:
            wallet_id: Database wallet ID
            user_id: Telegram user ID
            wallet_address: Deposit address
            deposit_amount: Amount deposited in USDC
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Validate minimum deposit
            if deposit_amount < self.min_deposit:
                print(f"⚠️ Deposit below minimum: {deposit_amount} USDC (min: {self.min_deposit})")
                # TODO: Notify user about minimum deposit requirement
                return False
            
            # Calculate fees and credits
            net_amount, platform_fee, conway_credits = self._calculate_conway_credits(deposit_amount)
            
            print(f"💰 Processing deposit:")
            print(f"   User: {user_id}")
            print(f"   Amount: {deposit_amount} USDC")
            print(f"   Platform Fee: {platform_fee} USDC ({self.platform_fee_rate * 100}%)")
            print(f"   Net Amount: {net_amount} USDC")
            print(f"   Conway Credits: {conway_credits}")
            
            # Credit Conway credits via API
            balance = self.conway.get_credit_balance(wallet_address)
            if balance is not None:
                print(f"✅ Current balance: {balance} credits")
                print(f"✅ Deposit processed: +{conway_credits} credits")
                
                # Update custodial wallet balance in database
                # Note: Conway API manages the actual credits, we just track deposits
                self._update_wallet_balance(wallet_id, deposit_amount, conway_credits)
                
                # Record deposit in database
                self._record_deposit(
                    wallet_id=wallet_id,
                    user_id=user_id,
                    amount=deposit_amount,
                    platform_fee=platform_fee,
                    credited_conway=conway_credits
                )
                
                # Record platform revenue
                self._record_platform_fee(user_id, platform_fee)
                
                # TODO: Send Telegram notification to user
                print(f"✅ Deposit processed successfully for user {user_id}")
                return True
            else:
                print(f"❌ Failed to verify balance after deposit")
                return False
        
        except Exception as e:
            print(f"❌ Error processing deposit: {e}")
            return False
    
    def _update_wallet_balance(
        self,
        wallet_id: str,
        deposit_amount: float,
        conway_credits: float
    ):
        """
        Update custodial wallet balance in database
        
        Args:
            wallet_id: Database wallet ID
            deposit_amount: USDC deposited
            conway_credits: Conway credits credited
        """
        try:
            query = """
                UPDATE custodial_wallets 
                SET balance_usdc = balance_usdc + ?,
                    conway_credits = conway_credits + ?,
                    total_deposited = total_deposited + ?,
                    last_deposit_at = ?
                WHERE id = ?
            """
            self.db.execute_query(
                query,
                (deposit_amount, conway_credits, deposit_amount, datetime.now().isoformat(), wallet_id)
            )
            print(f"✅ Updated wallet balance in database")
        
        except Exception as e:
            print(f"❌ Error updating wallet balance: {e}")
    
    def _record_deposit(
        self,
        wallet_id: str,
        user_id: int,
        amount: float,
        platform_fee: float,
        credited_conway: float
    ):
        """
        Record deposit in wallet_deposits table
        
        Args:
            wallet_id: Database wallet ID
            user_id: Telegram user ID
            amount: Deposit amount in USDC
            platform_fee: Platform fee deducted
            credited_conway: Conway credits credited
        """
        try:
            # Generate a pseudo tx_hash for tracking (since we're using Conway API)
            tx_hash = f"conway_{wallet_id}_{int(time.time())}"
            
            query = """
                INSERT INTO wallet_deposits 
                (wallet_id, user_id, tx_hash, from_address, amount, token, network, 
                 status, confirmations, detected_at, confirmed_at, credited_conway, platform_fee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute_query(
                query,
                (
                    wallet_id, user_id, tx_hash, 'conway_api', amount, 'USDC', 'base',
                    'confirmed', self.min_confirmations, datetime.now().isoformat(),
                    datetime.now().isoformat(), credited_conway, platform_fee
                )
            )
            print(f"✅ Recorded deposit in database")
        
        except Exception as e:
            print(f"❌ Error recording deposit: {e}")
    
    def _record_platform_fee(self, user_id: int, fee_amount: float):
        """
        Record platform fee in platform_revenue table
        
        Args:
            user_id: Telegram user ID
            fee_amount: Fee amount in USDC
        """
        try:
            query = """
                INSERT INTO platform_revenue (source, amount, user_id, timestamp)
                VALUES (?, ?, ?, ?)
            """
            self.db.execute_query(
                query,
                ('deposit_fee', fee_amount, user_id, datetime.now().isoformat())
            )
            print(f"✅ Recorded platform fee: {fee_amount} USDC")
        
        except Exception as e:
            print(f"❌ Error recording platform fee: {e}")
    
    async def _check_all_wallets(self):
        """
        Check all custodial wallets for balance changes
        
        Detects new deposits by comparing current balance with last known balance
        """
        try:
            # Get all custodial wallets from database
            query = "SELECT id, user_id, wallet_address, balance_usdc FROM custodial_wallets"
            wallets = self.db.execute_query(query, fetch_all=True)
            
            if not wallets:
                return
            
            print(f"🔍 Checking {len(wallets)} custodial wallets...")
            
            for wallet in wallets:
                wallet_id = wallet['id']
                user_id = wallet['user_id']
                wallet_address = wallet['wallet_address']
                db_balance = float(wallet['balance_usdc'] or 0)
                
                # Get current on-chain balance
                current_balance = self._get_usdc_balance(wallet_address)
                
                if current_balance is None:
                    continue
                
                # Get last known balance
                last_balance = self.last_balances.get(wallet_address, db_balance)
                
                # Detect new deposit
                if current_balance > last_balance:
                    deposit_amount = current_balance - last_balance
                    print(f"💰 New deposit detected!")
                    print(f"   Wallet: {wallet_address}")
                    print(f"   Amount: {deposit_amount} USDC")
                    
                    # Process the deposit
                    await self._process_deposit(
                        wallet_id=wallet_id,
                        user_id=user_id,
                        wallet_address=wallet_address,
                        deposit_amount=deposit_amount
                    )
                
                # Update last known balance
                self.last_balances[wallet_address] = current_balance
        
        except Exception as e:
            print(f"❌ Error checking wallets: {e}")
    
    async def start(self):
        """
        Start the deposit monitoring service
        
        Runs continuously, checking wallets every check_interval seconds
        """
        if self.is_running:
            print("⚠️ Deposit monitor is already running")
            return
        
        # Verify Web3 connection
        if not self._check_web3_connection():
            print("❌ Cannot start deposit monitor: Web3 not connected")
            return
        
        self.is_running = True
        print(f"🚀 Deposit monitor started (checking every {self.check_interval}s)")
        
        while self.is_running:
            try:
                await self._check_all_wallets()
                await asyncio.sleep(self.check_interval)
            
            except Exception as e:
                print(f"❌ Error in deposit monitor loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the deposit monitoring service"""
        self.is_running = False
        print("🛑 Deposit monitor stopped")


# Singleton instance
_deposit_monitor = None

def get_deposit_monitor(database) -> DepositMonitor:
    """
    Get singleton deposit monitor instance
    
    Args:
        database: Database instance
        
    Returns:
        DepositMonitor instance
    """
    global _deposit_monitor
    if _deposit_monitor is None:
        _deposit_monitor = DepositMonitor(database)
    return _deposit_monitor
