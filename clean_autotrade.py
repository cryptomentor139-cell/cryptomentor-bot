import os

def clean_autotrade_engine():
    filepath = r'd:\cryptomentorAI\Bismillah\app\autotrade_engine.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for i, line in enumerate(lines):
        # Remove the duplicated/misplaced section
        if "Enforce rule: Below $100 -> Auto 3% risk" in line:
            # We will re-insert this later in the correct spot
            for j in range(7): # skip the block
                lines[i+j] = ""
            continue
        
        # We find the real equity calculation
        if "equity = balance + unrealized_pnl" in line and "Enforce rule" not in lines[i+1]:
            new_lines.append(line)
            new_lines.append("\n")
            new_lines.append("            # Enforce rule: Below $100 -> Auto 3% risk for execution safety\n")
            new_lines.append("            if equity < 100:\n")
            new_lines.append("                if risk_pct != 3.0:\n")
            new_lines.append("                    logger.info(f\"[RiskCalc:{user_id}] Equity ${equity:.2f} < $100. Overriding risk {risk_pct}% -> 3.0% for execution safety.\")\n")
            new_lines.append("                    risk_pct = 3.0\n")
            continue
            
        if line.strip() != "":
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Cleaned up autotrade_engine.py")

clean_autotrade_engine()
