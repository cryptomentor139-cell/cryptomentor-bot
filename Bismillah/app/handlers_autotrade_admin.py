"""
Admin handlers for UID verification callbacks.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

try:
    from app.exchange_registry import get_exchange
    BITUNIX_GROUP_URL = get_exchange("bitunix").get("group_url")
except Exception:
    BITUNIX_GROUP_URL = os.getenv("BITUNIX_GROUP_URL", "")


def _is_admin(user_id: int) -> bool:
    admin_ids = set()
    for key in ("ADMIN_IDS", "ADMIN1", "ADMIN2", "ADMIN3", "ADMIN_USER_ID", "ADMIN2_USER_ID"):
        raw = os.getenv(key, "")
        for token in str(raw).split(","):
            token = token.strip()
            if token.isdigit():
                admin_ids.add(int(token))
    return user_id in admin_ids


def _load_existing_uid(s, user_id: int) -> str:
    """Fetch known UID from unified table first, then legacy mirror."""
    existing = (
        s.table("user_verifications")
        .select("bitunix_uid")
        .eq("telegram_id", user_id)
        .limit(1)
        .execute()
    )
    existing_uid = (existing.data or [{}])[0].get("bitunix_uid")
    if existing_uid:
        return str(existing_uid)

    legacy = (
        s.table("autotrade_sessions")
        .select("bitunix_uid")
        .eq("telegram_id", user_id)
        .limit(1)
        .execute()
    )
    legacy_uid = (legacy.data or [{}])[0].get("bitunix_uid")
    return str(legacy_uid or "unknown")


def _resolve_partner_owner_id(s, user_id: int) -> Optional[int]:
    """
    Resolve owning partner for this verification target.
    Priority:
    1) user_verifications.resolved_partner_telegram_id
    2) community_code -> active community_partners.telegram_id
    """
    try:
        ver = (
            s.table("user_verifications")
            .select("resolved_partner_telegram_id, community_code")
            .eq("telegram_id", int(user_id))
            .limit(1)
            .execute()
        )
    except Exception:
        # Backward compatibility for schemas that do not have resolved_partner_telegram_id yet.
        ver = (
            s.table("user_verifications")
            .select("community_code")
            .eq("telegram_id", int(user_id))
            .limit(1)
            .execute()
        )
    row = (ver.data or [None])[0]
    if not row:
        return None

    resolved_partner = row.get("resolved_partner_telegram_id")
    if resolved_partner is not None:
        try:
            return int(resolved_partner)
        except (TypeError, ValueError):
            logger.warning("Invalid resolved_partner_telegram_id for user %s: %s", user_id, resolved_partner)

    community_code = str(row.get("community_code") or "").strip().lower()
    if not community_code:
        return None

    partner = (
        s.table("community_partners")
        .select("telegram_id")
        .eq("community_code", community_code)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    partner_row = (partner.data or [None])[0]
    if not partner_row:
        return None
    try:
        return int(partner_row.get("telegram_id"))
    except (TypeError, ValueError):
        return None


def _is_authorized_reviewer(s, actor_id: int, target_user_id: int) -> Tuple[bool, str]:
    """Allow admin or owning partner to review UID callbacks."""
    if _is_admin(actor_id):
        return True, "admin"

    try:
        owner_id = _resolve_partner_owner_id(s, target_user_id)
    except Exception as exc:
        logger.error("Failed partner owner lookup for user=%s actor=%s: %s", target_user_id, actor_id, exc)
        return False, "lookup_failed"

    if owner_id is not None and int(owner_id) == int(actor_id):
        return True, "partner"
    return False, "unauthorized"


async def callback_uid_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        actor_id = query.from_user.id
        user_id = int(query.data.split("_")[-1])
        now_iso = datetime.now(timezone.utc).isoformat()

        from app.supabase_repo import _client

        s = _client()
        authorized, actor_role = _is_authorized_reviewer(s, actor_id, user_id)
        if not authorized:
            await query.edit_message_text("❌ Unauthorized: only admin or assigned community partner can review this UID.")
            return

        existing_uid = _load_existing_uid(s, user_id)

        # Central verification state used by website gatekeeper.
        s.table("user_verifications").upsert(
            {
                "telegram_id": user_id,
                "bitunix_uid": existing_uid,
                "status": "approved",
                "reviewed_at": now_iso,
                "reviewed_by_admin_id": actor_id,
                "updated_at": now_iso,
            },
            on_conflict="telegram_id",
        ).execute()

        # Legacy mirror for existing bot logic that still checks autotrade_sessions.
        s.table("autotrade_sessions").upsert(
            {
                "telegram_id": user_id,
                "status": "uid_verified",
                "updated_at": now_iso,
            },
            on_conflict="telegram_id",
        ).execute()
        logger.info("[UIDReview] approved user=%s reviewer=%s role=%s", user_id, actor_id, actor_role)

        from app.lib.auth import generate_dashboard_url

        dash_url = generate_dashboard_url(user_id)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🌐 Dashboard", url=dash_url)]]
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ <b>UID Verified!</b>\n\nReady to trade.",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        if BITUNIX_GROUP_URL:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🚀 <b>AutoTrade Setup Complete</b>\n\n"
                    "Great job — your onboarding is done.\n\n"
                    "✅ Next step:\n"
                    "Join our official community group to get updates, event announcements, and support.\n\n"
                    "Tap below to join:"
                ),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("👥 Join CryptoMentor x Bitunix Group", url=BITUNIX_GROUP_URL)]]
                ),
                disable_web_page_preview=True,
            )
        await query.edit_message_text(f"✅ Approved User {user_id}")
    except Exception as e:
        logger.error("Error in callback_uid_acc: %s", e)
        await query.edit_message_text(f"❌ Error: {e}")


async def callback_uid_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        actor_id = query.from_user.id
        user_id = int(query.data.split("_")[-1])
        now_iso = datetime.now(timezone.utc).isoformat()

        from app.supabase_repo import _client

        s = _client()
        authorized, actor_role = _is_authorized_reviewer(s, actor_id, user_id)
        if not authorized:
            await query.edit_message_text("❌ Unauthorized: only admin or assigned community partner can review this UID.")
            return

        existing_uid = _load_existing_uid(s, user_id)

        # Central verification state used by website gatekeeper.
        s.table("user_verifications").upsert(
            {
                "telegram_id": user_id,
                "bitunix_uid": existing_uid,
                "status": "rejected",
                "reviewed_at": now_iso,
                "reviewed_by_admin_id": actor_id,
                "updated_at": now_iso,
            },
            on_conflict="telegram_id",
        ).execute()

        # Legacy mirror for existing bot logic that still checks autotrade_sessions.
        s.table("autotrade_sessions").upsert(
            {
                "telegram_id": user_id,
                "status": "uid_rejected",
                "updated_at": now_iso,
            },
            on_conflict="telegram_id",
        ).execute()
        logger.info("[UIDReview] rejected user=%s reviewer=%s role=%s", user_id, actor_id, actor_role)

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ <b>UID Rejected</b>\n\nPlease retry with a valid UID.",
            parse_mode="HTML",
        )
        await query.edit_message_text(f"❌ Rejected User {user_id}")
    except Exception as e:
        logger.error("Error in callback_uid_reject: %s", e)
        await query.edit_message_text(f"❌ Error: {e}")
