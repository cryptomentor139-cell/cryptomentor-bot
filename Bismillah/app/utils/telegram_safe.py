
import re
from telegram.constants import ParseMode

# Escape semua karakter khusus MarkdownV2 (termasuk '-')
_MD_V2_SPECIALS = r'_*[]()~`>#+-=|{}.!'

def escape_md_v2(text: str) -> str:
    return re.sub(r'([\\_*\[\]\(\)~`>#+\-=\|{}\.\!])', r'\\\1', text.replace('-', r'\-'))

async def safe_reply(update, text: str, prefer_html: bool = True):
    """
    Coba kirim dengan HTML (paling toleran), fallback ke Markdown, lalu plain text.
    """
    msg = update.effective_message
    # 1) HTML
    if prefer_html:
        try:
            return await msg.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception:
            pass
    # 2) MarkdownV2 (escape dulu)
    try:
        esc = escape_md_v2(text)
        return await msg.reply_text(esc, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
    except Exception:
        pass
    # 3) Plain text
    return await msg.reply_text(text, disable_web_page_preview=True)

async def safe_edit(bot, chat_id: int, message_id: int, text: str, prefer_html: bool = True):
    # 1) HTML
    if prefer_html:
        try:
            return await bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            )
        except Exception:
            pass
    # 2) MarkdownV2
    try:
        esc = escape_md_v2(text)
        return await bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=esc, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
        )
    except Exception:
        pass
    # 3) Plain
    return await bot.edit_message_text(
        chat_id=chat_id, message_id=message_id,
        text=text, disable_web_page_preview=True
    )
