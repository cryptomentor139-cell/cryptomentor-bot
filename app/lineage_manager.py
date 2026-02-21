"""
Lineage Manager - Parent-Child Agent Relationships and Revenue Sharing

This module manages the hierarchical lineage system where agents can spawn children,
and parents receive 10% of their children's earnings. Revenue sharing is recursive,
flowing up the lineage tree.

Key Features:
- Register parent-child relationships
- Distribute 10% of child earnings to parents
- Query lineage trees and statistics
- Prevent circular references
- Support autonomous spawning by agents
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from app.supabase_conn import get_supabase_client
from app.conway_integration import ConwayIntegration

logger = logging.getLogger(__name__)


class LineageManager:
    """Manages parent-child agent lineage and revenue sharing"""
    
    def __init__(self):
        """Initialize with database and Conway API client"""
        self.supabase = get_supabase_client()
        self.conway = ConwayIntegration()
        self.MAX_LINEAGE_DEPTH = 10
        self.PARENT_SHARE_PERCENTAGE = Decimal('0.10')  # 10%
    
    async def register_child_agent(
        self,
        child_agent_id: str,
        parent_agent_id: str
    ) -> bool:
        """
        Register parent-child relationship when spawning from existing agent
        
        Args:
            child_agent_id: UUID of the child agent
            parent_agent_id: UUID of the parent agent
            
        Returns:
            True if registration successful, False otherwise
            
        Raises:
            ValueError: If circular reference detected or depth limit exceeded
        """
        try:
            # 1. Verify parent exists
            parent_response = self.supabase.table('user_automatons').select('*').eq('id', parent_agent_id).execute()
            if not parent_response.data:
                raise ValueError(f"Parent agent {parent_agent_id} not found")
            
            parent = parent_response.data[0]
            
            # 2. Check for circular reference
            if await self._would_create_cycle(parent_agent_id, child_agent_id):
                raise ValueError("Circular lineage reference detected")
            
            # 3. Check lineage depth limit
            depth = await self._get_lineage_depth(parent_agent_id)
            if depth >= self.MAX_LINEAGE_DEPTH:
                raise ValueError(f"Maximum lineage depth ({self.MAX_LINEAGE_DEPTH}) exceeded")
            
            # 4. Update child agent with parent reference
            update_response = self.supabase.table('user_automatons').update({
                'parent_agent_id': parent_agent_id
            }).eq('id', child_agent_id).execute()
            
            if not update_response.data:
                logger.error(f"Failed to update child agent {child_agent_id} with parent {parent_agent_id}")
                return False
            
            logger.info(f"Registered lineage: child={child_agent_id}, parent={parent_agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering child agent: {e}")
            raise
    
    def get_agent_lineage(self, agent_id: str) -> Dict:
        """
        Retrieve agent's lineage information
        
        Args:
            agent_id: UUID of the agent
            
        Returns:
            Dictionary with lineage information:
            - parent_agent_id: UUID of parent (if exists)
            - parent_name: Name of parent agent
            - children: List of child agent dictionaries
            - total_children_count: Number of direct children
            - total_revenue_from_children: Total credits received from children
        """
        try:
            # Get agent details
            agent_response = self.supabase.table('user_automatons').select('*').eq('id', agent_id).execute()
            if not agent_response.data:
                return {}
            
            agent = agent_response.data[0]
            
            # Get parent info if exists
            parent_info = None
            if agent.get('parent_agent_id'):
                parent_response = self.supabase.table('user_automatons').select('id, agent_name').eq(
                    'id', agent['parent_agent_id']
                ).execute()
                if parent_response.data:
                    parent_info = parent_response.data[0]
            
            # Get children
            children_response = self.supabase.table('user_automatons').select('*').eq(
                'parent_agent_id', agent_id
            ).execute()
            children = children_response.data or []
            
            return {
                'parent_agent_id': agent.get('parent_agent_id'),
                'parent_name': parent_info['agent_name'] if parent_info else None,
                'children': children,
                'total_children_count': len(children),
                'total_revenue_from_children': float(agent.get('total_children_revenue', 0))
            }
            
        except Exception as e:
            logger.error(f"Error getting agent lineage: {e}")
            return {}
    
    async def distribute_child_revenue(
        self,
        child_agent_id: str,
        child_earnings: float
    ) -> bool:
        """
        Distribute 10% of child's earnings to parent
        
        This is called whenever a child agent earns credits. The parent receives
        10% of the child's gross earnings, and this is recursive up the tree.
        
        Args:
            child_agent_id: UUID of the child agent that earned
            child_earnings: Amount of credits the child earned
            
        Returns:
            True if distribution successful, False otherwise
        """
        try:
            if child_earnings <= 0:
                logger.warning(f"Invalid child earnings: {child_earnings}")
                return False
            
            # 1. Get child agent details
            child_response = self.supabase.table('user_automatons').select('*').eq('id', child_agent_id).execute()
            if not child_response.data:
                logger.error(f"Child agent {child_agent_id} not found")
                return False
            
            child = child_response.data[0]
            
            # 2. Check if child has parent
            parent_agent_id = child.get('parent_agent_id')
            if not parent_agent_id:
                logger.debug(f"Child agent {child_agent_id} has no parent, skipping revenue share")
                return True  # Not an error, just no parent
            
            # 3. Calculate parent share (10%)
            parent_share = float(Decimal(str(child_earnings)) * self.PARENT_SHARE_PERCENTAGE)
            
            # 4. Verify child has sufficient credits
            if child['conway_credits'] < parent_share:
                logger.warning(f"Child {child_agent_id} has insufficient credits for parent share")
                return False
            
            # 5. Transfer credits from child to parent
            # Deduct from child
            new_child_balance = child['conway_credits'] - parent_share
            self.supabase.table('user_automatons').update({
                'conway_credits': new_child_balance
            }).eq('id', child_agent_id).execute()
            
            # Add to parent
            parent_response = self.supabase.table('user_automatons').select('*').eq('id', parent_agent_id).execute()
            if not parent_response.data:
                logger.error(f"Parent agent {parent_agent_id} not found")
                return False
            
            parent = parent_response.data[0]
            new_parent_balance = parent['conway_credits'] + parent_share
            new_parent_total_children_revenue = parent.get('total_children_revenue', 0) + parent_share
            
            self.supabase.table('user_automatons').update({
                'conway_credits': new_parent_balance,
                'total_children_revenue': new_parent_total_children_revenue
            }).eq('id', parent_agent_id).execute()
            
            # 6. Record lineage transaction
            self.supabase.table('lineage_transactions').insert({
                'parent_agent_id': parent_agent_id,
                'child_agent_id': child_agent_id,
                'child_earnings': child_earnings,
                'parent_share': parent_share,
                'share_percentage': float(self.PARENT_SHARE_PERCENTAGE * 100),
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            
            # 7. Record in automaton_transactions for both agents
            # Child transaction (negative)
            self.supabase.table('automaton_transactions').insert({
                'automaton_id': child_agent_id,
                'type': 'lineage_share',
                'amount': -parent_share,
                'description': f"10% revenue share to parent {parent['agent_name']}",
                'related_agent_id': parent_agent_id,
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            
            # Parent transaction (positive)
            self.supabase.table('automaton_transactions').insert({
                'automaton_id': parent_agent_id,
                'type': 'lineage_share',
                'amount': parent_share,
                'description': f"10% revenue share from child {child['agent_name']}",
                'related_agent_id': child_agent_id,
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            
            # 8. Notify parent owner
            await self._notify_parent_revenue(
                parent_agent_id=parent_agent_id,
                parent_user_id=parent['user_id'],
                child_name=child['agent_name'],
                earnings=child_earnings,
                share=parent_share
            )
            
            # 9. Recursive: parent's earnings trigger grandparent share
            # The parent_share becomes the parent's "earnings" for the next level
            await self.distribute_child_revenue(parent_agent_id, parent_share)
            
            logger.info(f"Distributed {parent_share} credits from child {child_agent_id} to parent {parent_agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error distributing child revenue: {e}")
            return False
    
    def calculate_parent_share(self, child_earnings: float) -> float:
        """
        Calculate parent's share: child_earnings × 0.10 (10%)
        
        Args:
            child_earnings: Amount the child earned
            
        Returns:
            Parent's 10% share
        """
        return float(Decimal(str(child_earnings)) * self.PARENT_SHARE_PERCENTAGE)
    
    async def get_lineage_tree(
        self,
        root_agent_id: str,
        max_depth: int = 3
    ) -> Dict:
        """
        Retrieve hierarchical tree of agent lineage up to max_depth levels
        
        Args:
            root_agent_id: UUID of the root agent
            max_depth: Maximum depth to traverse (default 3, max 10)
            
        Returns:
            Nested dictionary structure with children and their children
        """
        if max_depth > self.MAX_LINEAGE_DEPTH:
            max_depth = self.MAX_LINEAGE_DEPTH
        
        return await self._build_tree_recursive(root_agent_id, max_depth, 0)
    
    def get_lineage_statistics(self, agent_id: str) -> Dict:
        """
        Calculate lineage statistics for an agent
        
        Args:
            agent_id: UUID of the agent
            
        Returns:
            Dictionary with statistics:
            - direct_children_count: Number of direct children
            - total_descendants_count: Total descendants at all levels
            - total_revenue_from_lineage: Total credits received from lineage
            - average_child_performance: Average earnings of direct children
        """
        try:
            # Get agent
            agent_response = self.supabase.table('user_automatons').select('*').eq('id', agent_id).execute()
            if not agent_response.data:
                return {}
            
            agent = agent_response.data[0]
            
            # Get direct children
            children_response = self.supabase.table('user_automatons').select('*').eq(
                'parent_agent_id', agent_id
            ).execute()
            children = children_response.data or []
            direct_children_count = len(children)
            
            # Calculate total descendants recursively
            total_descendants = self._count_descendants_recursive(agent_id)
            
            # Get total revenue from lineage
            total_revenue = float(agent.get('total_children_revenue', 0))
            
            # Calculate average child performance
            if children:
                total_child_earnings = sum(float(child.get('total_earnings', 0)) for child in children)
                average_child_performance = total_child_earnings / len(children)
            else:
                average_child_performance = 0.0
            
            return {
                'direct_children_count': direct_children_count,
                'total_descendants_count': total_descendants,
                'total_revenue_from_lineage': total_revenue,
                'average_child_performance': average_child_performance
            }
            
        except Exception as e:
            logger.error(f"Error calculating lineage statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _would_create_cycle(self, parent_id: str, child_id: str) -> bool:
        """Check if adding this parent-child relationship would create a cycle"""
        # If parent_id is a descendant of child_id, it would create a cycle
        return await self._is_descendant(parent_id, child_id)
    
    async def _is_descendant(self, potential_descendant: str, ancestor: str) -> bool:
        """Check if potential_descendant is in the descendant tree of ancestor"""
        # Get all children of ancestor
        children_response = self.supabase.table('user_automatons').select('id, parent_agent_id').eq(
            'parent_agent_id', ancestor
        ).execute()
        
        if not children_response.data:
            return False
        
        for child in children_response.data:
            if child['id'] == potential_descendant:
                return True
            # Recursive check
            if await self._is_descendant(potential_descendant, child['id']):
                return True
        
        return False
    
    async def _get_lineage_depth(self, agent_id: str) -> int:
        """Calculate the depth of the lineage tree starting from this agent"""
        agent_response = self.supabase.table('user_automatons').select('parent_agent_id').eq('id', agent_id).execute()
        if not agent_response.data:
            return 0
        
        parent_id = agent_response.data[0].get('parent_agent_id')
        if not parent_id:
            return 0
        
        return 1 + await self._get_lineage_depth(parent_id)
    
    async def _build_tree_recursive(
        self,
        agent_id: str,
        max_depth: int,
        current_depth: int
    ) -> Dict:
        """Recursively build lineage tree"""
        # Get agent details
        agent_response = self.supabase.table('user_automatons').select('*').eq('id', agent_id).execute()
        if not agent_response.data:
            return {}
        
        agent = agent_response.data[0]
        
        tree = {
            'agent_id': agent['id'],
            'name': agent['agent_name'],
            'credits': float(agent['conway_credits']),
            'total_children_revenue': float(agent.get('total_children_revenue', 0)),
            'status': agent['status'],
            'survival_tier': agent['survival_tier'],
            'children': []
        }
        
        # If we haven't reached max depth, get children
        if current_depth < max_depth:
            children_response = self.supabase.table('user_automatons').select('id').eq(
                'parent_agent_id', agent_id
            ).execute()
            
            if children_response.data:
                for child in children_response.data:
                    child_tree = await self._build_tree_recursive(
                        child['id'],
                        max_depth,
                        current_depth + 1
                    )
                    tree['children'].append(child_tree)
        
        return tree
    
    def _count_descendants_recursive(self, agent_id: str) -> int:
        """Count total descendants at all levels"""
        children_response = self.supabase.table('user_automatons').select('id').eq(
            'parent_agent_id', agent_id
        ).execute()
        
        if not children_response.data:
            return 0
        
        count = len(children_response.data)
        for child in children_response.data:
            count += self._count_descendants_recursive(child['id'])
        
        return count
    
    async def _notify_parent_revenue(
        self,
        parent_agent_id: str,
        parent_user_id: int,
        child_name: str,
        earnings: float,
        share: float
    ):
        """Send Telegram notification to parent owner about revenue share"""
        try:
            # Import here to avoid circular dependency
            from telegram import Bot
            from telegram.constants import ParseMode
            import os
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                logger.warning("TELEGRAM_BOT_TOKEN not set, skipping notification")
                return
            
            bot = Bot(token=bot_token)
            
            message = (
                f"💰 <b>Lineage Revenue Received!</b>\n\n"
                f"Your agent received passive income from its child:\n\n"
                f"👶 <b>Child Agent:</b> {child_name}\n"
                f"💵 <b>Child Earnings:</b> {earnings:,.2f} credits\n"
                f"🎁 <b>Your Share (10%):</b> {share:,.2f} credits\n\n"
                f"💡 <i>Your agents earn while you sleep!</i>"
            )
            
            await bot.send_message(
                chat_id=parent_user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Error sending parent revenue notification: {e}")
