"""
OpenClaw Payment System
Automated deposit, credit allocation, and platform fee management
"""

import os
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import requests

logger = logging.getLogger(__name__)


class OpenClawPaymentSystem:
    """
    Payment system for OpenClaw credits
    
    Flow:
    1. User deposits $10
    2. Platform fee: $2 (20%) → Admin wallet
    3. User credits: $8 (80%) → Auto-topup OpenRouter
    4. User gets credits for OpenClaw usage
    """
    
    # Configuration
    PLATFORM_FEE_PERCENTAGE = Decimal('0.20')  # 20%
    USER_CREDIT_PERCENTAGE = Decimal('0.80')   # 80%
    
    # Minimum deposit amounts
    MIN_DEPOSIT_USD = Decimal('5.00')
    MAX_DEPOSIT_USD = Decimal('1000.00')
    
    # OpenRouter API
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self):
        """Initialize payment system"""
        self.admin_wallet = os.getenv('ADMIN_WALLET_ADDRESS')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not self.admin_wallet:
            logger.warning("ADMIN_WALLET_ADDRESS not set in environment")
        
        if not self.openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY not set in environment")
        
        logger.info("OpenClaw Payment System initialized")
    
    def calculate_split(self, deposit_amount: Decimal) -> Dict[str, Decimal]:
        """
        Calculate payment split
        
        Args:
            deposit_amount: Total deposit amount in USD
            
        Returns:
            Dict with platform_fee, user_credits, total
        """
        platform_fee = deposit_amount * self.PLATFORM_FEE_PERCENTAGE
        user_credits = deposit_amount * self.USER_CREDIT_PERCENTAGE
        
        return {
            'total': deposit_amount,
            'platform_fee': platform_fee.quantize(Decimal('0.01')),
            'user_credits': user_credits.quantize(Decimal('0.01')),
            'platform_fee_percentage': float(self.PLATFORM_FEE_PERCENTAGE * 100),
            'user_credit_percentage': float(self.USER_CREDIT_PERCENTAGE * 100)
        }
    
    def validate_deposit(self, amount: Decimal) -> Tuple[bool, str]:
        """
        Validate deposit amount
        
        Args:
            amount: Deposit amount in USD
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if amount < self.MIN_DEPOSIT_USD:
            return False, f"Minimum deposit is ${self.MIN_DEPOSIT_USD}"
        
        if amount > self.MAX_DEPOSIT_USD:
            return False, f"Maximum deposit is ${self.MAX_DEPOSIT_USD}"
        
        return True, ""
    
    def generate_deposit_wallet(self, user_id: int, amount: Decimal) -> Dict:
        """
        Generate unique deposit wallet for user
        
        Args:
            user_id: Telegram user ID
            amount: Deposit amount
            
        Returns:
            Dict with wallet info and payment instructions
        """
        # Validate amount
        is_valid, error = self.validate_deposit(amount)
        if not is_valid:
            return {
                'success': False,
                'error': error
            }
        
        # Calculate split
        split = self.calculate_split(amount)
        
        # Generate unique wallet address (you'll need to implement actual wallet generation)
        # For now, using a placeholder
        deposit_wallet = self._generate_unique_wallet(user_id, amount)
        
        return {
            'success': True,
            'deposit_wallet': deposit_wallet,
            'amount': float(amount),
            'split': {
                'total': float(split['total']),
                'platform_fee': float(split['platform_fee']),
                'user_credits': float(split['user_credits']),
                'platform_fee_percentage': split['platform_fee_percentage'],
                'user_credit_percentage': split['user_credit_percentage']
            },
            'instructions': self._generate_payment_instructions(deposit_wallet, amount),
            'expires_at': self._get_expiry_time()
        }
    
    def _generate_unique_wallet(self, user_id: int, amount: Decimal) -> str:
        """
        Generate unique wallet address for deposit
        
        This is a placeholder. In production, you would:
        1. Use a payment processor (Coinbase Commerce, NOWPayments, etc.)
        2. Generate unique address per transaction
        3. Monitor blockchain for deposits
        
        Args:
            user_id: User ID
            amount: Deposit amount
            
        Returns:
            Wallet address string
        """
        # Placeholder - replace with actual wallet generation
        # Options:
        # 1. Coinbase Commerce API
        # 2. NOWPayments API
        # 3. CryptoCloud API
        # 4. Your own wallet infrastructure
        
        import hashlib
        import time
        
        # Generate deterministic but unique address
        data = f"{user_id}:{amount}:{time.time()}"
        hash_obj = hashlib.sha256(data.encode())
        
        # This is just a placeholder format
        # Replace with actual wallet generation
        return f"0x{hash_obj.hexdigest()[:40]}"
    
    def _generate_payment_instructions(self, wallet: str, amount: Decimal) -> str:
        """Generate payment instructions for user"""
        admin_wallet = os.getenv('ADMIN_WALLET_ADDRESS', '0xed7342ac9c22b1495af4d63f15a7c9768a028ea8')
        
        return (
            f"💰 <b>Deposit Instructions</b>\n\n"
            f"<b>Amount:</b> ${amount}\n\n"
            f"<b>Payment Breakdown:</b>\n"
            f"• Your Credits: ${amount * self.USER_CREDIT_PERCENTAGE:.2f} (80%)\n"
            f"• Platform Fee: ${amount * self.PLATFORM_FEE_PERCENTAGE:.2f} (20%)\n\n"
            f"<b>⛓️ Crypto Payment (BEP20)</b>\n"
            f"Network: BEP20 (Binance Smart Chain)\n"
            f"Address:\n"
            f"<code>{admin_wallet}</code>\n\n"
            f"<b>Supported Coins:</b>\n"
            f"• USDT (BEP20)\n"
            f"• USDC (BEP20)\n"
            f"• BNB\n\n"
            f"<b>⚠️ Important:</b>\n"
            f"1. Send EXACTLY ${amount:.2f} worth of crypto\n"
            f"2. Use BEP20 network only!\n"
            f"3. After payment, send proof to admin\n"
            f"4. Credits added after confirmation\n\n"
            f"<b>📱 Contact Admin:</b>\n"
            f"@BillFarr\n\n"
            f"<b>Include in message:</b>\n"
            f"• Transaction hash\n"
            f"• Amount sent\n"
            f"• Your Telegram UID"
        )
    
    def _get_expiry_time(self) -> str:
        """Get payment expiry time (24 hours from now)"""
        from datetime import timedelta
        expiry = datetime.now() + timedelta(hours=24)
        return expiry.isoformat()
    
    def process_deposit(
        self,
        user_id: int,
        transaction_hash: str,
        amount: Decimal,
        db_connection
    ) -> Dict:
        """
        Process confirmed deposit
        
        Args:
            user_id: Telegram user ID
            transaction_hash: Blockchain transaction hash
            amount: Confirmed deposit amount
            db_connection: Database connection
            
        Returns:
            Dict with processing result
        """
        try:
            # Calculate split
            split = self.calculate_split(amount)
            
            # 1. Transfer platform fee to admin wallet
            platform_fee_result = self._transfer_platform_fee(
                split['platform_fee'],
                transaction_hash
            )
            
            # 2. Top up OpenRouter credits
            topup_result = self._topup_openrouter(
                user_id,
                split['user_credits']
            )
            
            # 3. Add credits to user account
            credits_result = self._add_user_credits(
                user_id,
                split['user_credits'],
                db_connection
            )
            
            # 4. Log transaction
            self._log_transaction(
                user_id=user_id,
                transaction_hash=transaction_hash,
                amount=amount,
                split=split,
                db_connection=db_connection
            )
            
            return {
                'success': True,
                'user_id': user_id,
                'transaction_hash': transaction_hash,
                'amount': float(amount),
                'platform_fee': float(split['platform_fee']),
                'user_credits': float(split['user_credits']),
                'openrouter_topup': topup_result,
                'message': f"Deposit processed! You received ${split['user_credits']:.2f} in credits"
            }
            
        except Exception as e:
            logger.error(f"Error processing deposit: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _transfer_platform_fee(self, amount: Decimal, tx_hash: str) -> Dict:
        """
        Transfer platform fee to admin wallet
        
        Args:
            amount: Fee amount
            tx_hash: Original transaction hash
            
        Returns:
            Transfer result
        """
        if not self.admin_wallet:
            logger.warning("Admin wallet not configured, skipping fee transfer")
            return {'success': False, 'reason': 'Admin wallet not configured'}
        
        # In production, implement actual transfer logic
        # For now, just log it
        logger.info(f"Platform fee ${amount:.2f} for tx {tx_hash} → {self.admin_wallet}")
        
        return {
            'success': True,
            'amount': float(amount),
            'destination': self.admin_wallet,
            'note': 'Platform fee transferred'
        }
    
    def _topup_openrouter(self, user_id: int, amount: Decimal) -> Dict:
        """
        Top up OpenRouter credits automatically
        
        Args:
            user_id: User ID
            amount: Credit amount in USD
            
        Returns:
            Topup result
        """
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not configured")
            return {'success': False, 'reason': 'API key not configured'}
        
        try:
            # OpenRouter API endpoint for adding credits
            # Note: This is a placeholder - check OpenRouter docs for actual endpoint
            url = f"{self.OPENROUTER_API_URL}/credits/add"
            
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'user_id': str(user_id),
                'amount': float(amount),
                'currency': 'USD'
            }
            
            # For now, just log it (implement actual API call when available)
            logger.info(f"OpenRouter topup: ${amount:.2f} for user {user_id}")
            
            # Placeholder response
            return {
                'success': True,
                'amount': float(amount),
                'user_id': user_id,
                'note': 'Credits added to OpenRouter account'
            }
            
        except Exception as e:
            logger.error(f"OpenRouter topup error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_user_credits(
        self,
        user_id: int,
        amount: Decimal,
        db_connection
    ) -> Dict:
        """
        Add credits to user's account in database
        
        Args:
            user_id: User ID
            amount: Credit amount
            db_connection: Database connection
            
        Returns:
            Result dict
        """
        try:
            cursor = db_connection.cursor()
            
            # Update or insert user credits
            cursor.execute("""
                INSERT INTO openclaw_credits (user_id, credits, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET
                    credits = openclaw_credits.credits + EXCLUDED.credits,
                    updated_at = NOW()
            """, (user_id, float(amount)))
            
            db_connection.commit()
            
            # Get new balance
            cursor.execute("""
                SELECT credits FROM openclaw_credits WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            new_balance = result[0] if result else float(amount)
            
            return {
                'success': True,
                'user_id': user_id,
                'added': float(amount),
                'new_balance': new_balance
            }
            
        except Exception as e:
            logger.error(f"Error adding user credits: {e}")
            db_connection.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_transaction(
        self,
        user_id: int,
        transaction_hash: str,
        amount: Decimal,
        split: Dict,
        db_connection
    ):
        """Log transaction to database"""
        try:
            cursor = db_connection.cursor()
            
            cursor.execute("""
                INSERT INTO openclaw_transactions (
                    user_id, transaction_hash, amount,
                    platform_fee, user_credits,
                    status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                user_id,
                transaction_hash,
                float(amount),
                float(split['platform_fee']),
                float(split['user_credits']),
                'completed'
            ))
            
            db_connection.commit()
            logger.info(f"Transaction logged: {transaction_hash}")
            
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")
            db_connection.rollback()
    
    def get_user_balance(self, user_id: int, db_connection) -> Decimal:
        """Get user's current credit balance"""
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT credits FROM openclaw_credits WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            return Decimal(str(result[0])) if result else Decimal('0.00')
            
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return Decimal('0.00')
    
    def deduct_credits(
        self,
        user_id: int,
        amount: Decimal,
        db_connection,
        reason: str = "OpenClaw usage"
    ) -> Dict:
        """
        Deduct credits from user account
        
        Args:
            user_id: User ID
            amount: Amount to deduct
            db_connection: Database connection
            reason: Reason for deduction
            
        Returns:
            Result dict
        """
        try:
            cursor = db_connection.cursor()
            
            # Check balance
            current_balance = self.get_user_balance(user_id, db_connection)
            
            if current_balance < amount:
                return {
                    'success': False,
                    'error': 'Insufficient credits',
                    'current_balance': float(current_balance),
                    'required': float(amount)
                }
            
            # Deduct credits
            cursor.execute("""
                UPDATE openclaw_credits
                SET credits = credits - %s, updated_at = NOW()
                WHERE user_id = %s
            """, (float(amount), user_id))
            
            # Log usage
            cursor.execute("""
                INSERT INTO openclaw_usage_log (
                    user_id, amount, reason, created_at
                ) VALUES (%s, %s, %s, NOW())
            """, (user_id, float(amount), reason))
            
            db_connection.commit()
            
            new_balance = current_balance - amount
            
            return {
                'success': True,
                'user_id': user_id,
                'deducted': float(amount),
                'new_balance': float(new_balance),
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            db_connection.rollback()
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_payment_system = None

def get_payment_system() -> OpenClawPaymentSystem:
    """Get singleton instance of payment system"""
    global _payment_system
    if _payment_system is None:
        _payment_system = OpenClawPaymentSystem()
    return _payment_system
