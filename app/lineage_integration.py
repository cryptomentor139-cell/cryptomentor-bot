"""
Lineage Integration Helper

Helper functions to integrate lineage system with existing handlers and managers.
"""

import logging
from typing import Optional, Dict, List
from app.lineage_manager import LineageManager

logger = logging.getLogger(__name__)

# Global lineage manager instance
_lineage_manager = None


def get_lineage_manager() -> LineageManager:
    """Get or create lineage manager instance"""
    global _lineage_manager
    if _lineage_manager is None:
        _lineage_manager = LineageManager()
    return _lineage_manager


async def register_agent_lineage(child_agent_id: str, parent_agent_id: Optional[str]) -> bool:
    """
    Register parent-child relationship after agent spawn
    
    Args:
        child_agent_id: UUID of newly spawned agent
        parent_agent_id: UUID of parent agent (None if no parent)
        
    Returns:
        True if registration successful or no parent, False on error
    """
    if not parent_agent_id:
        # No parent, this is a root agent
        return True
    
    try:
        lineage_manager = get_lineage_manager()
        success = await lineage_manager.register_child_agent(child_agent_id, parent_agent_id)
        
        if success:
            logger.info(f"Lineage registered: child={child_agent_id}, parent={parent_agent_id}")
        else:
            logger.error(f"Failed to register lineage: child={child_agent_id}, parent={parent_agent_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error registering lineage: {e}")
        return False


async def distribute_agent_earnings(agent_id: str, earnings: float) -> bool:
    """
    Distribute earnings to parent agents (10% recursive)
    
    Call this after an agent earns credits (trading profit, etc.)
    
    Args:
        agent_id: UUID of agent that earned
        earnings: Amount of credits earned
        
    Returns:
        True if distribution successful, False on error
    """
    if earnings <= 0:
        return True  # Nothing to distribute
    
    try:
        lineage_manager = get_lineage_manager()
        success = await lineage_manager.distribute_child_revenue(agent_id, earnings)
        
        if success:
            logger.info(f"Earnings distributed: agent={agent_id}, amount={earnings}")
        else:
            logger.warning(f"Failed to distribute earnings: agent={agent_id}, amount={earnings}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error distributing earnings: {e}")
        return False


def get_agent_lineage_info(agent_id: str) -> Dict:
    """
    Get lineage information for an agent
    
    Args:
        agent_id: UUID of agent
        
    Returns:
        Dictionary with lineage info:
        - parent_agent_id: UUID of parent (if exists)
        - parent_name: Name of parent agent
        - children: List of child agents
        - total_children_count: Number of direct children
        - total_revenue_from_children: Total credits from children
    """
    try:
        lineage_manager = get_lineage_manager()
        return lineage_manager.get_agent_lineage(agent_id)
    except Exception as e:
        logger.error(f"Error getting lineage info: {e}")
        return {}


def get_agent_lineage_stats(agent_id: str) -> Dict:
    """
    Get lineage statistics for an agent
    
    Args:
        agent_id: UUID of agent
        
    Returns:
        Dictionary with statistics:
        - direct_children_count: Number of direct children
        - total_descendants_count: Total descendants at all levels
        - total_revenue_from_lineage: Total credits from lineage
        - average_child_performance: Average earnings of children
    """
    try:
        lineage_manager = get_lineage_manager()
        return lineage_manager.get_lineage_statistics(agent_id)
    except Exception as e:
        logger.error(f"Error getting lineage stats: {e}")
        return {}


async def get_agent_lineage_tree(agent_id: str, max_depth: int = 3) -> Dict:
    """
    Get hierarchical lineage tree for an agent
    
    Args:
        agent_id: UUID of root agent
        max_depth: Maximum depth to traverse (default 3)
        
    Returns:
        Nested dictionary with agent and children
    """
    try:
        lineage_manager = get_lineage_manager()
        return await lineage_manager.get_lineage_tree(agent_id, max_depth)
    except Exception as e:
        logger.error(f"Error getting lineage tree: {e}")
        return {}


def format_lineage_tree_text(tree: Dict, indent: int = 0) -> str:
    """
    Format lineage tree as text for display
    
    Args:
        tree: Tree dictionary from get_agent_lineage_tree
        indent: Current indentation level
        
    Returns:
        Formatted text representation
    """
    if not tree:
        return "No lineage data"
    
    lines = []
    prefix = "  " * indent
    
    # Agent info
    name = tree.get('name', 'Unknown')
    credits = tree.get('credits', 0)
    children_revenue = tree.get('total_children_revenue', 0)
    status = tree.get('status', 'unknown')
    tier = tree.get('survival_tier', 'unknown')
    
    # Status emoji
    tier_emoji = {
        'normal': '🟢',
        'low_compute': '🟡',
        'critical': '🔴',
        'dead': '⚫'
    }
    emoji = tier_emoji.get(tier, '⚪')
    
    # Format agent line
    agent_line = f"{prefix}🤖 {name}"
    lines.append(agent_line)
    lines.append(f"{prefix}├─ {emoji} {tier.upper()}")
    lines.append(f"{prefix}├─ 💰 {credits:,.0f} credits")
    if children_revenue > 0:
        lines.append(f"{prefix}├─ 👶 Revenue from children: {children_revenue:,.0f}")
    
    # Children
    children = tree.get('children', [])
    if children:
        lines.append(f"{prefix}└─ Children ({len(children)}):")
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            child_prefix = "   " if is_last else "│  "
            child_text = format_lineage_tree_text(child, indent + 1)
            lines.append(child_text)
    
    return "\n".join(lines)


def get_user_agents_with_lineage(user_id: int, db) -> List[Dict]:
    """
    Get user's agents with lineage information included
    
    Args:
        user_id: Telegram user ID
        db: Database instance
        
    Returns:
        List of agent dictionaries with lineage info added
    """
    try:
        # Get agents from database (existing function)
        from app.automaton_manager import get_automaton_manager
        automaton_manager = get_automaton_manager(db)
        agents = automaton_manager.get_user_agents(user_id)
        
        # Add lineage info to each agent
        for agent in agents:
            agent_id = agent.get('agent_id')
            if agent_id:
                lineage_info = get_agent_lineage_info(agent_id)
                agent['lineage'] = lineage_info
        
        return agents
        
    except Exception as e:
        logger.error(f"Error getting agents with lineage: {e}")
        return []


# Integration hooks for existing code

async def on_agent_spawn(agent_id: str, parent_agent_id: Optional[str] = None):
    """
    Hook to call after agent spawn
    
    Args:
        agent_id: Newly spawned agent ID
        parent_agent_id: Parent agent ID (if spawning from parent)
    """
    if parent_agent_id:
        await register_agent_lineage(agent_id, parent_agent_id)


async def on_agent_earn(agent_id: str, earnings: float):
    """
    Hook to call after agent earns credits
    
    Args:
        agent_id: Agent that earned
        earnings: Amount earned
    """
    await distribute_agent_earnings(agent_id, earnings)


async def on_performance_fee_collected(agent_id: str, profit: float, fee: float):
    """
    Hook to call after platform collects performance fee
    
    This is called AFTER platform takes 20% fee.
    The profit parameter is the GROSS profit (before fee).
    
    Args:
        agent_id: Agent that made profit
        profit: Gross profit amount
        fee: Platform fee collected (20% of profit)
    """
    # Distribute based on gross profit (before platform fee)
    # Parent gets 10% of gross, not net
    await distribute_agent_earnings(agent_id, profit)
