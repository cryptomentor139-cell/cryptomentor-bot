#!/usr/bin/env python3
"""Deep check of what data the dashboard actually shows."""
import paramiko
import json

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

def run(ssh, cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    return out

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)

    # Get token
    login_raw = run(ssh, "curl -s -X POST http://localhost:8896/auth/login -H 'Content-Type: application/json' -d '{\"password\": \"secret4896\"}'")
    token = json.loads(login_raw)["token"]

    # Full trading stats
    print("=== FULL Trading Stats (7 days) ===")
    stats_raw = run(ssh, f'curl -s "http://localhost:8896/api/analytics/trading-stats" -H "Authorization: Bearer {token}"')
    stats = json.loads(stats_raw)
    users = stats.get("users", {})
    print(f"Total users: {len(users)}")
    print(f"{'User ID':<15} {'Total':>6} {'Open':>5} {'Closed':>7} {'PnL USDT':>10} {'Win%':>7}")
    print("-" * 60)
    for uid, s in sorted(users.items()):
        print(f"{str(uid):<15} {s['total_trades']:>6} {s['open_positions']:>5} {s['closed_positions']:>7} {s['total_pnl_usdt']:>10.2f} {s['win_rate']:>6.1f}%")

    # Full engine health
    print("\n=== Engine Health ===")
    eng_raw = run(ssh, f'curl -s "http://localhost:8896/api/analytics/engine-health" -H "Authorization: Bearer {token}"')
    eng = json.loads(eng_raw)
    engines = eng.get("engines", {})
    running = sum(1 for e in engines.values() if e["running"])
    stopped = sum(1 for e in engines.values() if not e["running"])
    print(f"Running: {running}, Stopped: {stopped}, Total: {len(engines)}")

    # Check what file is actually running on VPS
    print("\n=== Analytics API file on VPS (key sections) ===")
    out = run(ssh, "grep -n 'CLOSED_STATUSES' /root/cryptomentor-bot/Bismillah/analytics_api.py")
    print("CLOSED_STATUSES lines:", out)

    # Check if there are recent errors in the logs
    print("\n=== Any ERROR lines in recent journal ===")
    out = run(ssh, "journalctl -u cryptomentor-analytics -n 100 --no-pager | grep -i 'error\\|exception\\|traceback' | tail -20")
    print(out or "(no errors)")

    # Check what nginx is sending (test via domain)
    print("\n=== HTTPS check ===")
    out = run(ssh, "curl -s -o /dev/null -w '%{http_code}' https://analytics4896.cryptomentor.id/health 2>&1")
    print(f"HTTPS health status: {out}")

    ssh.close()

if __name__ == "__main__":
    main()
