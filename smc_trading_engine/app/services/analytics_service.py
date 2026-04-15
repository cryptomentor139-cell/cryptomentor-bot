def build_decision_trace(context: dict, decision: dict) -> dict:
    return {
        "symbol": context.get("symbol"),
        "decision": decision.get("action"),
        "confidence": decision.get("confidence_score"),
        "reason": decision.get("reason"),
    }
