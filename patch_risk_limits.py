import os

def patch_file(filepath, target, replacement):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if target in content:
        new_content = content.replace(target, replacement, 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched {filepath}")
    else:
        print(f"Target not found in {filepath}")

# 1. Patch scalping_engine.py
scalping_file = r'd:\cryptomentorAI\Bismillah\app\scalping_engine.py'
scalping_target = "            balance = bal_result.get('balance', 0)"
scalping_replacement = """            balance = bal_result.get('balance', 0)
            
            # Enforce rule: Below $100 -> Auto 3% risk for execution safety
            if balance < 100:
                if risk_pct != 3.0:
                    logger.info(f"[Scalping:{self.user_id}] Balance ${balance:.2f} < $100. Overriding risk {risk_pct}% -> 3.0% for execution safety.")
                    risk_pct = 3.0"""

patch_file(scalping_file, scalping_target, scalping_replacement)

# 2. Patch autotrade_engine.py
autotrade_file = r'd:\cryptomentorAI\Bismillah\app\autotrade_engine.py'
autotrade_target = "            balance = available + frozen"
autotrade_replacement = """            balance = available + frozen
            # Equity = Total Balance + Unrealized P&L
            equity = balance + unrealized_pnl

            # Enforce rule: Below $100 -> Auto 3% risk for execution safety
            if equity < 100:
                if risk_pct != 3.0:
                    logger.info(f"[RiskCalc:{user_id}] Equity ${equity:.2f} < $100. Overriding risk {risk_pct}% -> 3.0% for execution safety.")
                    risk_pct = 3.0"""

patch_file(autotrade_file, autotrade_target, autotrade_replacement)
