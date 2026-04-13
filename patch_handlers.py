import os

def patch_handlers():
    filepath = r'd:\cryptomentorAI\Bismillah\app\handlers_autotrade.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update callback_risk_settings
    target1 = """    # Check marks for current selection
    check_1 = "✅ " if current_risk == 1.0 else ""
    check_2 = "✅ " if current_risk == 2.0 else ""
    check_3 = "✅ " if current_risk == 3.0 else ""
    check_5 = "✅ " if current_risk == 5.0 else ""
    
    await query.edit_message_text(
        f"🎯 <b>Risk Management Settings</b>\\n\\n"
        f"💰 Current Balance: <b>${balance:.2f}</b>\\n"
        f"{risk_info}\\n"
        f"💡 Recommended for your balance: <b>{recommended}%</b>\\n\\n"
        f"<b>What is Risk Per Trade?</b>\\n"
        f"Instead of fixed margin, you choose how much % of your balance to risk per trade. "
        f"This enables safe compounding and protects your account.\\n\\n"
        f"<b>Example:</b> Balance $100, Risk 2%\\n"
        f"• Max loss per trade: $2\\n"
        f"• Position size auto-calculated based on stop loss\\n"
        f"• As balance grows, position size grows too\\n\\n"
        f"Select your risk level:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"{check_1}🛡️ 1%", callback_data="at_set_risk_1"),
                InlineKeyboardButton(f"{check_2}⚖️ 2%", callback_data="at_set_risk_2"),
            ],
            [
                InlineKeyboardButton(f"{check_3}⚡ 3%", callback_data="at_set_risk_3"),
                InlineKeyboardButton(f"{check_5}🔥 5%", callback_data="at_set_risk_5"),
            ],
            [InlineKeyboardButton("📚 Learn More", callback_data="at_risk_edu")],
            [InlineKeyboardButton("🧮 Simulator", callback_data="at_risk_sim")],
            [InlineKeyboardButton("🔙 Back", callback_data="at_settings")],
        ])
    )"""

    # Note: Escaping for Python multi-line string
    replacement1 = """    # Enforce rules for the menu display
    is_small_account = balance < 100
    
    # Check marks for current selection
    check_05 = "✅ " if current_risk == 0.5 else ""
    check_1 = "✅ " if current_risk == 1.0 else ""
    check_2 = "✅ " if current_risk == 2.0 else ""
    check_3 = "✅ " if current_risk == 3.0 else ""
    check_5 = "✅ " if current_risk == 5.0 else ""
    check_10 = "✅ " if current_risk == 10.0 else ""
    
    if is_small_account:
        msg_text = (
            f"🎯 <b>Risk Management Settings</b>\\n\\n"
            f"💰 Current Balance: <b>${balance:.2f}</b>\\n"
            f"⚠️ <b>Account Balance Filter:</b>\\n"
            f"Your balance is below $100. To ensure trade execution meets exchange "
            f"minimum quantity requirements, your risk is <b>locked at 3%</b>.\\n\\n"
            f"<i>Increasing your balance to $100+ will unlock conservative risk settings (0.5% - 1.0%).</i>"
        )
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3% (Standard for Small Balance)", callback_data="at_set_risk_3")],
            [InlineKeyboardButton("📚 Learn More", callback_data="at_risk_edu")],
            [InlineKeyboardButton("🔙 Back", callback_data="at_settings")],
        ]
    else:
        msg_text = (
            f"🎯 <b>Risk Management Settings</b>\\n\\n"
            f"💰 Current Balance: <b>${balance:.2f}</b>\\n"
            f"{risk_info}\\n"
            f"💡 Recommended for your balance: <b>{recommended}%</b>\\n\\n"
            f"<b>Select your risk level:</b>"
        )
        keyboard = [
            [
                InlineKeyboardButton(f"{check_05}🛡️ 0.5%", callback_data="at_set_risk_0.5"),
                InlineKeyboardButton(f"{check_1}🛡️ 1%", callback_data="at_set_risk_1"),
            ],
            [
                InlineKeyboardButton(f"{check_2}⚖️ 2%", callback_data="at_set_risk_2"),
                InlineKeyboardButton(f"{check_3}⚡ 3%", callback_data="at_set_risk_3"),
            ],
            [
                InlineKeyboardButton(f"{check_5}🔥 5%", callback_data="at_set_risk_5"),
                InlineKeyboardButton(f"{check_10}💀 10%", callback_data="at_set_risk_10"),
            ],
            [InlineKeyboardButton("📚 Learn More", callback_data="at_risk_edu")],
            [InlineKeyboardButton("🧮 Simulator", callback_data="at_risk_sim")],
            [InlineKeyboardButton("🔙 Back", callback_data="at_settings")],
        ]

    await query.edit_message_text(
        msg_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )"""

    # 2. Update risk_map in callback_set_risk
    target2 = """    risk_map = {
        "at_set_risk_1": 1.0,
        "at_set_risk_2": 2.0,
        "at_set_risk_3": 3.0,
        "at_set_risk_5": 5.0,
    }"""
    
    replacement2 = """    risk_map = {
        "at_set_risk_0.5": 0.5,
        "at_set_risk_1": 1.0,
        "at_set_risk_2": 2.0,
        "at_set_risk_3": 3.0,
        "at_set_risk_5": 5.0,
        "at_set_risk_10": 10.0,
    }"""

    # Perform replacements (handling potential formatting issues by doing it per block)
    if target1 in content:
        content = content.replace(target1, replacement1)
    else:
        print("Target 1 not found")
        # Try a more fuzzy match for target 1
        import re
        content = re.sub(r'# Check marks for current selection.*?at_settings"\]\],\s+\)\s+\)', replacement1, content, flags=re.DOTALL)

    if target2 in content:
        content = content.replace(target2, replacement2)
    else:
        print("Target 2 not found")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched handlers_autotrade.py")

patch_handlers()
