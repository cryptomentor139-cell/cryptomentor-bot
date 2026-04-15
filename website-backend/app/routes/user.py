import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
from app.auth.jwt import decode_token
from app.db.supabase import get_user_by_tid, _client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])
bearer = HTTPBearer()


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])

class SubmitUIDRequest(BaseModel):
    uid: str
    community_code: str | None = None  # ?ref= value captured on landing


VER_PENDING = "pending"
VER_APPROVED = "approved"
VER_REJECTED = "rejected"

_APPROVED_ALIASES = {VER_APPROVED, "uid_verified", "active", "verified"}
_PENDING_ALIASES = {VER_PENDING, "pending_verification", "awaiting_approval"}
_REJECTED_ALIASES = {VER_REJECTED, "uid_rejected", "denied"}


def _normalize_verification_status(raw_status: str) -> str:
    status = str(raw_status or "").strip().lower()
    if status in _APPROVED_ALIASES:
        return VER_APPROVED
    if status in _PENDING_ALIASES:
        return VER_PENDING
    if status in _REJECTED_ALIASES:
        return VER_REJECTED
    return status or "none"


def _load_admin_ids() -> list[int]:
    """Load admin IDs from multiple env keys for resilience."""
    ids = set()
    raw_values = [
        os.getenv("ADMIN_IDS", ""),
        os.getenv("ADMIN1", ""),
        os.getenv("ADMIN2", ""),
        os.getenv("ADMIN_USER_ID", ""),
        os.getenv("ADMIN2_USER_ID", ""),
    ]
    for raw in raw_values:
        for token in str(raw).split(","):
            token = token.strip()
            if token.isdigit():
                ids.add(int(token))
    return sorted(ids)


def _sanitize_community_code(raw: str | None) -> str | None:
    code = str(raw or "").strip().lower()
    if not code:
        return None
    return "".join(ch for ch in code if ch.isalnum())[:32] or None


def _fallback_referral_url() -> str:
    return os.getenv(
        "FALLBACK_REFERRAL_URL",
        "https://www.bitunix.com/register?vipCode=yongdnf",
    )


def _query_user_verification_row(s, tg_id: int) -> dict | None:
    """
    Read verification row while tolerating partially-migrated schemas.
    """
    try:
        res = (
            s.table("user_verifications")
            .select("status, bitunix_uid, submitted_via, reviewed_at, reviewed_by_admin_id, community_code, bitunix_referral_url, ref_source, partner_telegram_id")
            .eq("telegram_id", tg_id)
            .limit(1)
            .execute()
        )
        return (res.data or [None])[0]
    except Exception as exc:
        logger.warning(
            "[Verification] Extended select failed for tg_id=%s, falling back to legacy columns: %s",
            tg_id,
            exc,
        )
        res = (
            s.table("user_verifications")
            .select("status, bitunix_uid, submitted_via, reviewed_at, reviewed_by_admin_id")
            .eq("telegram_id", tg_id)
            .limit(1)
            .execute()
        )
        return (res.data or [None])[0]


def _upsert_user_verification(s, payload: dict, tg_id: int) -> None:
    """
    Upsert verification row with compatibility fallback for old DB schemas.
    """
    try:
        s.table("user_verifications").upsert(payload, on_conflict="telegram_id").execute()
        return
    except Exception as exc:
        logger.warning(
            "[Verification] Extended upsert failed for tg_id=%s, retrying legacy payload: %s",
            tg_id,
            exc,
        )

    legacy_payload = {
        "telegram_id": payload.get("telegram_id"),
        "bitunix_uid": payload.get("bitunix_uid"),
        "status": payload.get("status"),
        "submitted_via": payload.get("submitted_via"),
        "submitted_at": payload.get("submitted_at"),
    }
    # Keep reviewed metadata when present in legacy schema.
    if payload.get("reviewed_at") is not None:
        legacy_payload["reviewed_at"] = payload.get("reviewed_at")
    if payload.get("reviewed_by_admin_id") is not None:
        legacy_payload["reviewed_by_admin_id"] = payload.get("reviewed_by_admin_id")

    s.table("user_verifications").upsert(legacy_payload, on_conflict="telegram_id").execute()


def _resolve_referral_context(community_code: str | None) -> dict:
    """
    Resolve referral destination from community_code with centralized fallback.
    """
    s = _client()
    partner_telegram_id = None
    partner_name = None
    partner_referral_url = None
    ref_source = "fallback"
    normalized_code = _sanitize_community_code(community_code)

    if normalized_code:
        try:
            partner_res = (
                s.table("community_partners")
                .select("id, telegram_id, community_name, community_code, bitunix_referral_url, status")
                .eq("community_code", normalized_code)
                .eq("status", "active")
                .limit(1)
                .execute()
            )
            partner_record = (partner_res.data or [None])[0]
            if partner_record:
                partner_telegram_id = partner_record.get("telegram_id")
                partner_name = partner_record.get("community_name")
                partner_referral_url = partner_record.get("bitunix_referral_url")
                ref_source = "dynamic"
                logger.info(
                    "[Referral] Resolved partner: code=%s partner_id=%s url=%s",
                    normalized_code, partner_telegram_id, partner_referral_url,
                )
            else:
                logger.warning(
                    "[Referral] community_code=%s did not resolve to an active partner — using fallback",
                    normalized_code,
                )
        except Exception as e:
            logger.error("[Referral] Partner lookup failed for code=%s: %s", normalized_code, e)

    if not partner_referral_url:
        partner_referral_url = _fallback_referral_url()
        logger.warning(
            "[Referral] Using fallback referral URL ref_source=fallback code=%s url=%s",
            normalized_code, partner_referral_url,
        )

    return {
        "community_code": normalized_code,
        "partner_telegram_id": partner_telegram_id,
        "partner_name": partner_name,
        "bitunix_referral_url": partner_referral_url,
        "ref_source": ref_source,
    }

@router.get("/me")
async def get_me(tg_id: int = Depends(get_current_user)):
    user = get_user_by_tid(tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/verification-status")
async def get_verification_status(tg_id: int = Depends(get_current_user)):
    """Single source of truth: user_verifications in Supabase."""
    admin_ids = _load_admin_ids()
    if tg_id in admin_ids:
        return {"status": VER_APPROVED, "exchange": "bitunix", "uid": None}

    s = _client()
    row = _query_user_verification_row(s, tg_id)
    if not row:
        fallback_url = _fallback_referral_url()
        return {
            "status": "none",
            "exchange": None,
            "uid": None,
            "community_code": None,
            "bitunix_referral_url": fallback_url,
            "ref_source": "fallback",
            "partner_telegram_id": None,
        }
    normalized_status = _normalize_verification_status(row.get("status"))
    return {
        "status": normalized_status,
        "raw_status": row.get("status") or "none",
        "exchange": "bitunix",
        "uid": row.get("bitunix_uid"),
        "submitted_via": row.get("submitted_via"),
        "reviewed_at": row.get("reviewed_at"),
        "reviewed_by_admin_id": row.get("reviewed_by_admin_id"),
        "community_code": row.get("community_code"),
        "bitunix_referral_url": row.get("bitunix_referral_url") or _fallback_referral_url(),
        "ref_source": row.get("ref_source") or "fallback",
        "partner_telegram_id": row.get("partner_telegram_id"),
    }


@router.get("/referral-context")
async def get_referral_context(
    community_code: str | None = None,
    tg_id: int = Depends(get_current_user),
):
    """
    Resolve a partner referral context for onboarding/gatekeeper UI.
    """
    _ = tg_id  # explicit auth gate; value intentionally unused.
    return _resolve_referral_context(community_code)

@router.post("/submit-uid")
async def submit_uid(payload: SubmitUIDRequest, tg_id: int = Depends(get_current_user)):
    """Submit Bitunix UID for admin verification and notify admins."""
    uid = str(payload.uid or "").strip()
    if not uid.isdigit() or len(uid) < 5:
        raise HTTPException(status_code=400, detail="Invalid UID. Must be numeric and at least 5 digits.")

    # Sanitize community_code from payload
    community_code = _sanitize_community_code(payload.community_code)

    s = _client()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Check current verification status (central source).
    res = (
        s.table("user_verifications")
        .select("status")
        .eq("telegram_id", tg_id)
        .limit(1)
        .execute()
    )
    row = (res.data or [None])[0]
    current_status = _normalize_verification_status(row.get("status") if row else "none")
    if current_status == VER_APPROVED:
        raise HTTPException(status_code=400, detail="Your UID is already verified.")

    # --- Resolve community partner from community_code ---
    resolved = _resolve_referral_context(community_code)
    partner_telegram_id = resolved["partner_telegram_id"]
    partner_name = resolved["partner_name"]
    partner_referral_url = resolved["bitunix_referral_url"]
    ref_source = resolved["ref_source"]

    # Store verification with full referral context.
    _upsert_user_verification(
        s,
        {
            "telegram_id": tg_id,
            "bitunix_uid": uid,
            "status": VER_PENDING,
            "submitted_via": "web",
            "submitted_at": now_iso,
            "community_code": community_code,
            "partner_telegram_id": partner_telegram_id,
            "bitunix_referral_url": partner_referral_url,
            "ref_source": ref_source,
            "reviewed_at": None,
            "reviewed_by_admin_id": None,
            "rejection_reason": None,
            "updated_at": now_iso,
        },
        tg_id=tg_id,
    )

    # Backward compatibility for legacy flows still reading autotrade_sessions.
    try:
        s.table("autotrade_sessions").upsert(
            {
                "telegram_id": tg_id,
                "exchange": "bitunix",
                "bitunix_uid": uid,
                "status": "pending_verification",
                "updated_at": now_iso,
            },
            on_conflict="telegram_id",
        ).execute()
    except Exception:
        logger.warning("Failed to mirror pending status into autotrade_sessions for tg_id=%s", tg_id)

    # Get user info for richer admin notification
    user = get_user_by_tid(tg_id)
    username = user.get("username") or user.get("first_name") or str(tg_id) if user else str(tg_id)
    resubmit_note = " (resubmission after rejection)" if current_status == VER_REJECTED else ""

    # Build notification message with full referral context
    partner_line = (
        f"🤝 Community: <b>{partner_name}</b> (<code>{community_code}</code>)\n"
        if partner_name else "🤝 Community: <i>none / fallback</i>\n"
    )
    referral_line = f"🔗 Referral URL: <code>{partner_referral_url}</code>\n"
    ref_source_line = f"📌 Ref Source: <b>{ref_source}</b>\n"

    notification_text = (
        f"🔔 <b>New UID Verification{resubmit_note}</b>\n\n"
        f"👤 User: @{username} (ID: <code>{tg_id}</code>)\n"
        f"🔑 Bitunix UID: <code>{uid}</code>\n"
        f"{partner_line}"
        f"{referral_line}"
        f"{ref_source_line}"
        f"🕐 Time: {now_iso[:19]}Z"
    )

    # Admin + partner notification
    admin_ids = _load_admin_ids()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    notification_failed = False

    # Collect all recipients: admins + community partner (if resolved)
    recipient_ids = list(admin_ids)
    if partner_telegram_id and partner_telegram_id not in recipient_ids:
        recipient_ids.append(partner_telegram_id)

    if bot_token and recipient_ids:
        async with httpx.AsyncClient(timeout=8.0) as client:
            for recipient_id in recipient_ids:
                # Partner gets slightly different message (no approve/reject buttons — admin only)
                is_admin = recipient_id in admin_ids
                try:
                    payload = {
                        "chat_id": recipient_id,
                        "text": notification_text,
                        "parse_mode": "HTML",
                    }
                    if is_admin:
                        payload["reply_markup"] = {"inline_keyboard": [[
                            {"text": "✅ Approve", "callback_data": f"uid_acc_{tg_id}"},
                            {"text": "❌ Reject", "callback_data": f"uid_reject_{tg_id}"}
                        ]]}
                    resp = await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json=payload,
                    )
                    if resp.status_code >= 400:
                        notification_failed = True
                        logger.error("Telegram sendMessage failed: status=%s body=%s", resp.status_code, resp.text[:300])
                        continue

                    body = resp.json() if resp.text else {}
                    if not body.get("ok", False):
                        notification_failed = True
                        logger.error("Telegram sendMessage API returned ok=false: %s", str(body)[:300])
                except Exception as e:
                    notification_failed = True
                    logger.error("Telegram sendMessage exception for recipient_id=%s: %s", recipient_id, e)
    else:
        # Keep user pending but surface notification pipeline issue.
        notification_failed = True
        logger.error("Telegram notification skipped: bot_token_missing=%s admin_ids=%s", not bool(bot_token), admin_ids)

    if notification_failed:
        return {
            "status": VER_PENDING,
            "uid": uid,
            "community_code": community_code,
            "bitunix_referral_url": partner_referral_url,
            "ref_source": ref_source,
            "warning": "UID submitted and pending, but admin notification failed. Please contact support/admin.",
        }

    return {
        "status": VER_PENDING,
        "uid": uid,
        "community_code": community_code,
        "bitunix_referral_url": partner_referral_url,
        "ref_source": ref_source,
    }

@router.get("/dashboard")
async def get_dashboard(tg_id: int = Depends(get_current_user)):
    """Data ringkasan untuk halaman dashboard website."""
    user = get_user_by_tid(tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "telegram_id": user.get("telegram_id"),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "credits": user.get("credits", 0),
        "is_premium": user.get("is_premium", False),
        "premium_until": user.get("premium_until"),
        "is_lifetime": user.get("is_lifetime", False),
    }
