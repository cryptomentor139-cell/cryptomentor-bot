#!/usr/bin/env python3
"""
Signal Performance Analyzer
Analyze completed signals to find patterns and optimize parameters
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any

def load_completed_signals(days: int = 30) -> List[Dict]:
    """Load completed signals from last N days"""
    log_dir = Path("signal_logs")
    completed_file = log_dir / "completed_signals.jsonl"
    
    if not completed_file.exists():
        print("❌ No completed signals found")
        return []
    
    signals = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with open(completed_file, "r") as f:
        for line in f:
            try:
                signal = json.loads(line)
                signal_date = datetime.fromisoformat(signal.get('created_at', ''))
                if signal_date >= cutoff_date:
                    signals.append(signal)
            except:
                continue
    
    return signals

def calculate_winrate(signals: List[Dict]) -> Dict[str, Any]:
    """Calculate overall winrate"""
    if not signals:
        return {"total": 0, "wins": 0, "losses": 0, "winrate": 0, "avg_pnl": 0}
    
    wins = [s for s in signals if s.get('result') == 'WIN']
    losses = [s for s in signals if s.get('result') == 'LOSS']
    
    total = len(signals)
    win_count = len(wins)
    loss_count = len(losses)
    winrate = (win_count / total * 100) if total > 0 else 0
    
    pnls = [s.get('pnl_percent', 0) for s in signals]
    avg_pnl = sum(pnls) / len(pnls) if pnls else 0
    
    return {
        "total": total,
        "wins": win_count,
        "losses": loss_count,
        "winrate": winrate,
        "avg_pnl": avg_pnl
    }

def analyze_by_coin(signals: List[Dict]) -> Dict[str, Dict]:
    """Analyze performance by coin"""
    by_coin = defaultdict(list)
    
    for signal in signals:
        symbol = signal.get('symbol', 'UNKNOWN')
        by_coin[symbol].append(signal)
    
    results = {}
    for symbol, coin_signals in by_coin.items():
        results[symbol] = calculate_winrate(coin_signals)
    
    # Sort by winrate
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['winrate'], reverse=True))
    return sorted_results

def analyze_by_signal_type(signals: List[Dict]) -> Dict[str, Dict]:
    """Analyze performance by LONG vs SHORT"""
    by_type = defaultdict(list)
    
    for signal in signals:
        signal_type = signal.get('signal_type', 'UNKNOWN')
        by_type[signal_type].append(signal)
    
    results = {}
    for sig_type, type_signals in by_type.items():
        results[sig_type] = calculate_winrate(type_signals)
    
    return results

def analyze_by_timeframe(signals: List[Dict]) -> Dict[str, Dict]:
    """Analyze performance by timeframe"""
    by_tf = defaultdict(list)
    
    for signal in signals:
        timeframe = signal.get('timeframe', 'UNKNOWN')
        by_tf[timeframe].append(signal)
    
    results = {}
    for tf, tf_signals in by_tf.items():
        results[tf] = calculate_winrate(tf_signals)
    
    return results

def find_best_performers(signals: List[Dict], top_n: int = 5) -> List[str]:
    """Find top performing coins"""
    by_coin = analyze_by_coin(signals)
    
    # Filter coins with at least 5 signals
    filtered = {k: v for k, v in by_coin.items() if v['total'] >= 5}
    
    # Sort by winrate
    sorted_coins = sorted(filtered.items(), key=lambda x: x[1]['winrate'], reverse=True)
    
    return [coin for coin, _ in sorted_coins[:top_n]]

def find_worst_performers(signals: List[Dict], bottom_n: int = 5) -> List[str]:
    """Find worst performing coins"""
    by_coin = analyze_by_coin(signals)
    
    # Filter coins with at least 5 signals
    filtered = {k: v for k, v in by_coin.items() if v['total'] >= 5}
    
    # Sort by winrate (ascending)
    sorted_coins = sorted(filtered.items(), key=lambda x: x[1]['winrate'])
    
    return [coin for coin, _ in sorted_coins[:bottom_n]]

def generate_recommendations(signals: List[Dict]) -> List[str]:
    """Generate optimization recommendations based on data"""
    recommendations = []
    
    overall = calculate_winrate(signals)
    by_coin = analyze_by_coin(signals)
    by_type = analyze_by_signal_type(signals)
    
    # Check overall winrate
    if overall['winrate'] < 60:
        recommendations.append("⚠️ Overall winrate below 60% - Consider increasing MIN_CONFIDENCE threshold")
    elif overall['winrate'] > 75:
        recommendations.append("✅ Excellent winrate! System is performing well")
    
    # Check LONG vs SHORT
    if 'LONG' in by_type and 'SHORT' in by_type:
        long_wr = by_type['LONG']['winrate']
        short_wr = by_type['SHORT']['winrate']
        
        if abs(long_wr - short_wr) > 15:
            if long_wr > short_wr:
                recommendations.append(f"📊 LONG signals ({long_wr:.1f}%) outperform SHORT ({short_wr:.1f}%) - Consider focusing on LONG")
            else:
                recommendations.append(f"📊 SHORT signals ({short_wr:.1f}%) outperform LONG ({long_wr:.1f}%) - Consider focusing on SHORT")
    
    # Check coin performance
    best = find_best_performers(signals, 3)
    worst = find_worst_performers(signals, 3)
    
    if best:
        recommendations.append(f"🏆 Best performers: {', '.join(best)} - Prioritize these coins")
    
    if worst:
        worst_coins_data = {coin: by_coin[coin] for coin in worst if coin in by_coin}
        low_winrate_coins = [coin for coin, data in worst_coins_data.items() if data['winrate'] < 50]
        if low_winrate_coins:
            recommendations.append(f"❌ Poor performers (<50% WR): {', '.join(low_winrate_coins)} - Consider excluding")
    
    # Check sample size
    if overall['total'] < 50:
        recommendations.append(f"⏳ Only {overall['total']} signals - Collect more data (target: 100+) for reliable analysis")
    
    return recommendations

def print_analysis_report(signals: List[Dict], days: int = 30):
    """Print comprehensive analysis report"""
    print("\n" + "="*60)
    print(f"📊 SIGNAL PERFORMANCE ANALYSIS ({days} DAYS)")
    print("="*60)
    
    # Overall performance
    overall = calculate_winrate(signals)
    print(f"\n📈 OVERALL PERFORMANCE")
    print(f"   Total Signals: {overall['total']}")
    print(f"   Wins: {overall['wins']} ✅")
    print(f"   Losses: {overall['losses']} ❌")
    print(f"   Winrate: {overall['winrate']:.1f}% 🎯")
    print(f"   Avg PnL: {overall['avg_pnl']:+.2f}%")
    
    # By signal type
    by_type = analyze_by_signal_type(signals)
    print(f"\n📊 BY SIGNAL TYPE")
    for sig_type, stats in by_type.items():
        print(f"   {sig_type}:")
        print(f"      Signals: {stats['total']}")
        print(f"      Winrate: {stats['winrate']:.1f}%")
        print(f"      Avg PnL: {stats['avg_pnl']:+.2f}%")
    
    # By coin (top 10)
    by_coin = analyze_by_coin(signals)
    print(f"\n🪙 TOP 10 COINS BY WINRATE")
    for i, (coin, stats) in enumerate(list(by_coin.items())[:10], 1):
        if stats['total'] >= 3:  # At least 3 signals
            print(f"   {i}. {coin}: {stats['winrate']:.1f}% ({stats['total']} signals)")
    
    # Best performers
    best = find_best_performers(signals, 5)
    if best:
        print(f"\n🏆 BEST PERFORMERS (≥5 signals)")
        for coin in best:
            stats = by_coin[coin]
            print(f"   {coin}: {stats['winrate']:.1f}% WR, {stats['avg_pnl']:+.2f}% avg PnL ({stats['total']} signals)")
    
    # Worst performers
    worst = find_worst_performers(signals, 5)
    if worst:
        print(f"\n❌ WORST PERFORMERS (≥5 signals)")
        for coin in worst:
            stats = by_coin[coin]
            print(f"   {coin}: {stats['winrate']:.1f}% WR, {stats['avg_pnl']:+.2f}% avg PnL ({stats['total']} signals)")
    
    # Recommendations
    recommendations = generate_recommendations(signals)
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS")
        for rec in recommendations:
            print(f"   {rec}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    import sys
    
    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except:
            pass
    
    print(f"🔍 Loading signals from last {days} days...")
    signals = load_completed_signals(days)
    
    if not signals:
        print("❌ No completed signals found!")
        print("\n💡 Signals need to be marked as completed (WIN/LOSS) first")
        print("   Use: update_signal_outcome(signal_id, hit_tp=True/False, pnl_percent=X)")
        sys.exit(1)
    
    print(f"✅ Loaded {len(signals)} completed signals")
    
    print_analysis_report(signals, days)
    
    print("\n💡 Usage:")
    print("   python analyze_signal_performance.py [days]")
    print("   Example: python analyze_signal_performance.py 7  # Last 7 days")
