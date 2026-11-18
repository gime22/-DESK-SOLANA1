"""Strict, fail-closed Solana memecoin screening before any live-trade proposal.

This module does NOT claim token safety, make network calls, or place orders.
Every safety input must come from an actual verified source; missing data = SKIP.
"""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

MAX_AGE_HOURS = 24
MIN_LIQUIDITY_USD = Decimal("20000")
MIN_VOLUME_24H_USD = Decimal("50000")
MIN_HOLDERS = 100
MAX_TOP10_HOLDER_PCT = Decimal("35")
MAX_POSITION_SOL = Decimal("0.05")

def numeric(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
        return result if result.is_finite() and result >= 0 else None
    except (InvalidOperation, ValueError):
        return None

def evaluate(observation, now_ms=None):
    """Return decision and immutable reasons. Never infer missing facts."""
    if now_ms is None:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    reasons = []
    created = numeric(observation.get("created_at_ms"))
    if created is None or created > now_ms or now_ms - created > MAX_AGE_HOURS * 3600000:
        reasons.append("Token not verified as launched within 0-24h")
    liq = numeric(observation.get("liquidity_usd"))
    if liq is None or liq < MIN_LIQUIDITY_USD:
        reasons.append("Liquidity missing or below $20,000")
    vol = numeric(observation.get("volume_24h_usd"))
    if vol is None or vol < MIN_VOLUME_24H_USD:
        reasons.append("24h volume missing or below $50,000")
    holders = numeric(observation.get("holders"))
    if holders is None or holders < MIN_HOLDERS or holders != holders.to_integral_value():
        reasons.append("Verified holder count missing or below 100")
    top10 = numeric(observation.get("top10_holder_pct"))
    if top10 is None or top10 > MAX_TOP10_HOLDER_PCT:
        reasons.append("Top-10 holder concentration missing or above 35%")
    for key in ("mint_authority_disabled", "freeze_authority_disabled", "sellable", "smart_money_verified"):
        if observation.get(key) is not True:
            reasons.append(key + " not positively verified")
    sources = observation.get("verification_sources")
    if not isinstance(sources, dict) or any(not isinstance(sources.get(k), str) or not sources[k].strip() for k in ("holders", "contract", "smart_money", "market")):
        reasons.append("Required verification source references missing")
    # 'WATCHLIST' is not trade approval; human review and Moby guardrails still required.
    return {"decision": "SKIP" if reasons else "WATCHLIST_MANUAL_REVIEW", "reasons": reasons, "live_trading_allowed": False}
