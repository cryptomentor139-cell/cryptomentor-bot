# Audit Logger - Security and Compliance Logging
# Logs all sensitive operations for security auditing and compliance

import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client


class AuditLogger:
    """
    Manages audit logging for sensitive operations
    
    Features:
    - Log private key decryption events
    - Log admin operations
    - Log fee collections
    - Log withdrawal requests
    - Store in separate audit_logs table
    
    Security:
    - Never logs sensitive data (private keys, passwords)
    - Logs only metadata (timestamp, user_id, operation_type)
    - Immutable audit trail
    """
    
    def __init__(self, db=None):
        """
        Initialize Audit Logger
        
        Args:
            db: Database instance (optional, will use Supabase directly)
        """
        self.db = db
        
        # Initialize Supabase client for audit logging
        self.supabase_enabled = False
        try:
            supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
            
            if supabase_url and supabase_key:
                self.supabase = create_client(supabase_url, supabase_key)
                self.supabase_enabled = True
                print("✅ Audit Logger initialized with Supabase")
            else:
                print("⚠️ Audit Logger: Supabase credentials not found")
        except Exception as e:
            print(f"❌ Audit Logger initialization error: {e}")
            self.supabase_enabled = False
    
    def log_private_key_decryption(
        self,
        wallet_address: str,
        operation_type: str,
        admin_id: int,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Log private key decryption event
        
        Args:
            wallet_address: Wallet address being accessed
            operation_type: Type of operation (withdrawal, transfer, etc.)
            admin_id: Admin telegram ID performing the operation
            success: Whether decryption was successful
            error_message: Optional error message if failed
            
        Returns:
            True if logged successfully
        """
        try:
            if not self.supabase_enabled:
                print("⚠️ Audit logging disabled: Supabase not available")
                return False
            
            audit_entry = {
                'event_type': 'private_key_decryption',
                'wallet_address': wallet_address,
                'operation_type': operation_type,
                'admin_id': admin_id,
                'success': success,
                'error_message': error_message,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'operation': operation_type,
                    'wallet': wallet_address
                }
            }
            
            self.supabase.table('audit_logs').insert(audit_entry).execute()
            
            print(f"🔒 Audit: Private key decryption - Wallet: {wallet_address}, "
                  f"Operation: {operation_type}, Admin: {admin_id}, Success: {success}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error logging private key decryption: {e}")
            return False
    
    def log_admin_operation(
        self,
        admin_id: int,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        target_user_id: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Log admin operation
        
        Args:
            admin_id: Admin telegram ID
            command: Command executed
            parameters: Command parameters (sanitized)
            target_user_id: Target user ID if applicable
            success: Whether operation was successful
            error_message: Optional error message if failed
            
        Returns:
            True if logged successfully
        """
        try:
            if not self.supabase_enabled:
                print("⚠️ Audit logging disabled: Supabase not available")
                return False
            
            # Sanitize parameters to remove sensitive data
            safe_params = self._sanitize_parameters(parameters) if parameters else {}
            
            audit_entry = {
                'event_type': 'admin_operation',
                'admin_id': admin_id,
                'command': command,
                'parameters': safe_params,
                'target_user_id': target_user_id,
                'success': success,
                'error_message': error_message,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'command': command,
                    'target': target_user_id
                }
            }
            
            self.supabase.table('audit_logs').insert(audit_entry).execute()
            
            print(f"👮 Audit: Admin operation - Admin: {admin_id}, Command: {command}, "
                  f"Target: {target_user_id}, Success: {success}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error logging admin operation: {e}")
            return False
    
    def log_fee_collection(
        self,
        fee_type: str,
        amount: float,
        agent_id: Optional[str] = None,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Log fee collection event
        
        Args:
            fee_type: Type of fee (deposit_fee, performance_fee, withdrawal_fee)
            amount: Fee amount collected
            agent_id: Agent UUID if applicable
            user_id: User telegram ID
            description: Optional description
            
        Returns:
            True if logged successfully
        """
        try:
            if not self.supabase_enabled:
                print("⚠️ Audit logging disabled: Supabase not available")
                return False
            
            audit_entry = {
                'event_type': 'fee_collection',
                'fee_type': fee_type,
                'amount': amount,
                'agent_id': agent_id,
                'user_id': user_id,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'type': fee_type,
                    'amount': amount,
                    'agent': agent_id
                }
            }
            
            self.supabase.table('audit_logs').insert(audit_entry).execute()
            
            print(f"💰 Audit: Fee collection - Type: {fee_type}, Amount: {amount:,.2f}, "
                  f"Agent: {agent_id}, User: {user_id}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error logging fee collection: {e}")
            return False
    
    def log_withdrawal_request(
        self,
        user_id: int,
        amount: float,
        to_address: str,
        token: str = 'USDT',
        status: str = 'pending',
        withdrawal_id: Optional[str] = None
    ) -> bool:
        """
        Log withdrawal request
        
        Args:
            user_id: User telegram ID
            amount: Withdrawal amount
            to_address: Destination address
            token: Token type (USDT, USDC)
            status: Withdrawal status
            withdrawal_id: Withdrawal UUID if available
            
        Returns:
            True if logged successfully
        """
        try:
            if not self.supabase_enabled:
                print("⚠️ Audit logging disabled: Supabase not available")
                return False
            
            audit_entry = {
                'event_type': 'withdrawal_request',
                'user_id': user_id,
                'amount': amount,
                'to_address': to_address,
                'token': token,
                'status': status,
                'withdrawal_id': withdrawal_id,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'amount': amount,
                    'token': token,
                    'destination': to_address[:10] + '...' + to_address[-8:]  # Truncate for privacy
                }
            }
            
            self.supabase.table('audit_logs').insert(audit_entry).execute()
            
            print(f"💸 Audit: Withdrawal request - User: {user_id}, Amount: {amount} {token}, "
                  f"To: {to_address[:10]}...{to_address[-8:]}, Status: {status}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error logging withdrawal request: {e}")
            return False
    
    def log_deposit_detection(
        self,
        user_id: int,
        wallet_address: str,
        amount: float,
        token: str,
        tx_hash: Optional[str] = None,
        network: str = 'polygon'
    ) -> bool:
        """
        Log deposit detection event
        
        Args:
            user_id: User telegram ID
            wallet_address: Custodial wallet address
            amount: Deposit amount
            token: Token type (USDT, USDC)
            tx_hash: Transaction hash
            network: Network name
            
        Returns:
            True if logged successfully
        """
        try:
            if not self.supabase_enabled:
                print("⚠️ Audit logging disabled: Supabase not available")
                return False
            
            audit_entry = {
                'event_type': 'deposit_detection',
                'user_id': user_id,
                'wallet_address': wallet_address,
                'amount': amount,
                'token': token,
                'tx_hash': tx_hash,
                'network': network,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'amount': amount,
                    'token': token,
                    'network': network
                }
            }
            
            self.supabase.table('audit_logs').insert(audit_entry).execute()
            
            print(f"📥 Audit: Deposit detection - User: {user_id}, Amount: {amount} {token}, "
                  f"Network: {network}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error logging deposit detection: {e}")
            return False
    
    def log_agent_spawn(
        self,
        user_id: int,
        agent_id: str,
        agent_name: str,
        credits_deducted: float,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Log agent spawn event
        
        Args:
            user_id: User telegram ID
            agent_id: Agent UUID
            agent_name: Agent name
            credits_deducted: Credits deducted for spawn
            success: Whether spawn was successful
            error_message: Optional error message if failed
            
        Returns:
            True if logged successfully
        """
        try:
            if not self.supabase_enabled:
                print("⚠️ Audit logging disabled: Supabase not available")
                return False
            
            audit_entry = {
                'event_type': 'agent_spawn',
                'user_id': user_id,
                'agent_id': agent_id,
                'agent_name': agent_name,
                'credits_deducted': credits_deducted,
                'success': success,
                'error_message': error_message,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'agent_name': agent_name,
                    'credits': credits_deducted
                }
            }
            
            self.supabase.table('audit_logs').insert(audit_entry).execute()
            
            print(f"🤖 Audit: Agent spawn - User: {user_id}, Agent: {agent_name}, "
                  f"Credits: {credits_deducted}, Success: {success}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error logging agent spawn: {e}")
            return False
    
    def get_audit_logs(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        limit: int = 100
    ) -> list:
        """
        Retrieve audit logs with filters
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            admin_id: Filter by admin ID
            limit: Maximum number of records to return
            
        Returns:
            List of audit log entries
        """
        try:
            if not self.supabase_enabled:
                return []
            
            query = self.supabase.table('audit_logs').select('*')
            
            if event_type:
                query = query.eq('event_type', event_type)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            if admin_id:
                query = query.eq('admin_id', admin_id)
            
            result = query.order('timestamp', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
        
        except Exception as e:
            print(f"❌ Error retrieving audit logs: {e}")
            return []
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize parameters to remove sensitive data
        
        Args:
            parameters: Raw parameters
            
        Returns:
            Sanitized parameters
        """
        sensitive_keys = [
            'password', 'private_key', 'secret', 'token', 'api_key',
            'encryption_key', 'mnemonic', 'seed'
        ]
        
        sanitized = {}
        for key, value in parameters.items():
            # Check if key contains sensitive terms
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        
        return sanitized


# Singleton instance
_audit_logger = None


def get_audit_logger(db=None):
    """
    Get singleton Audit Logger instance
    
    Args:
        db: Database instance (optional)
        
    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(db)
    return _audit_logger
