import logging

logger = logging.getLogger("smc.audit")


def log_decision(symbol: str, payload: dict) -> None:
    logger.info("decision symbol=%s payload=%s", symbol, payload)
