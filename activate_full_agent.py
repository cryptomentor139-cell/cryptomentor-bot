"""
Quick Activation Script for Full Autonomous Agent
Run this to integrate agent into your bot
"""

import os
import sys

def check_files():
    """Check if all required files exist"""
    required_files = [
        'app/openclaw_agent_tools.py',
        'app/openclaw_agent_loop.py',
        'app/openclaw_manager.py',
        'app/openclaw_message_handler.py',
        'bot.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("❌ Missing required files:")
        for file in missing:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def show_integration_steps():
    """Show integration steps"""
    print("\n" + "="*60)
    print("🤖 FULL AUTONOMOUS AGENT - INTEGRATION STEPS")
    print("="*60)
    
    print("\n📋 Step 1: Update bot.py")
    print("-" * 60)
    print("""
Add these imports at the top:

from app.openclaw_agent_tools import get_openclaw_agent_tools
from app.openclaw_agent_loop import get_openclaw_agentic_loop
""")
    
    print("\n📋 Step 2: Initialize Agent in main()")
    print("-" * 60)
    print("""
After initializing openclaw_manager, add:

# Initialize autonomous agent
agent_tools = get_openclaw_agent_tools(db, application)
agentic_loop = get_openclaw_agentic_loop(openclaw_manager, agent_tools)

logger.info("✅ Autonomous agent initialized")
""")
    
    print("\n📋 Step 3: Update OpenClawMessageHandler")
    print("-" * 60)
    print("""
In openclaw_message_handler.py, modify the chat call:

# Find this line:
response, tokens_in, tokens_out, cost = self.manager.chat(...)

# Replace with:
if hasattr(self, 'agentic_loop') and self.agentic_loop:
    response, tokens_in, tokens_out, cost, tool_calls = \\
        self.agentic_loop.chat_with_tools(
            user_id=user_id,
            assistant_id=assistant_id,
            message=message_text,
            conversation_id=conversation_id
        )
    
    # Show tool usage
    if tool_calls:
        tools_used = [tc['tool'] for tc in tool_calls]
        await update.message.reply_text(
            f"🔧 Tools used: {', '.join(tools_used)}"
        )
else:
    # Fallback to basic chat
    response, tokens_in, tokens_out, cost = self.manager.chat(...)
""")
    
    print("\n📋 Step 4: Pass agentic_loop to handler")
    print("-" * 60)
    print("""
When creating OpenClawMessageHandler:

# Find this:
openclaw_handler = OpenClawMessageHandler(openclaw_manager)

# Update to:
openclaw_handler = OpenClawMessageHandler(openclaw_manager)
openclaw_handler.agentic_loop = agentic_loop
""")
    
    print("\n📋 Step 5: Test")
    print("-" * 60)
    print("""
1. Run bot locally: python bot.py
2. Login as admin
3. Start OpenClaw: /openclaw_start
4. Test commands:
   - "Show me bot statistics"
   - "What are current prices?"
   - "Get info for user 123456"
   - "Show system information"
""")
    
    print("\n📋 Step 6: Deploy")
    print("-" * 60)
    print("""
1. Commit changes:
   git add .
   git commit -m "Activate full autonomous agent"
   git push

2. Deploy to Railway:
   railway up

3. Monitor logs for agent activity
""")
    
    print("\n" + "="*60)
    print("📚 Documentation:")
    print("   - FULL_AGENT_READY.md - Overview & status")
    print("   - FULL_AGENT_IMPLEMENTATION_PLAN.md - Detailed plan")
    print("="*60)

def main():
    print("\n🤖 Full Autonomous Agent - Activation Script")
    print("=" * 60)
    
    # Check files
    if not check_files():
        print("\n❌ Cannot proceed - missing files")
        sys.exit(1)
    
    # Show integration steps
    show_integration_steps()
    
    print("\n✅ Ready to integrate!")
    print("\nFollow the steps above to activate the autonomous agent.")
    print("Need help? Check FULL_AGENT_READY.md\n")

if __name__ == "__main__":
    main()
