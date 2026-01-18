from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from database import is_premium
from upsell import upsell_after_delete
from ai_spam import is_spam
import re
import logging

# ───────────── ESCALATION SETTINGS ─────────────
WARN_LIMIT = 1
MUTE_LIMIT = 2
BAN_LIMIT = 3
MUTE_DURATION = 600  # 10 minutes

# ───────────── WARNING STORAGE ─────────────
warnings = {}  # {chat_id: {user_id: count}}

# ───────────── SPAM DETECTION ─────────────
SPAM_KEYWORDS = ["free", "money", "click here", "promo", "win"]

# Strong URL detection (http, https, www, shortened links)
URL_PATTERN = re.compile(r"(?i)\b((?:https?://|www\.)\S+)")

# Telegram invites (t.me/joinchat/... or t.me/+xxxx)
INVITE_PATTERN = re.compile(r"(?i)t\.me/joinchat/|telegram\.me/joinchat/|t\.me/\+")

# ───────────── MODERATION FUNCTION ─────────────
async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    chat_id = update.effective_chat.id
    user_id = msg.from_user.id

    # ───────────── IGNORE ADMINS ─────────────
    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status in ("administrator", "creator"):
        return

    # ───────────── GET MESSAGE TEXT OR CAPTION ─────────────
    text = msg.text or msg.caption or ""

    # ───────────── DETECT SPAM / LINKS ─────────────
    is_text_spam = is_spam(text)
    is_url_spam = bool(URL_PATTERN.search(text) or INVITE_PATTERN.search(text))
    is_keyword_spam = any(word in text.lower() for word in SPAM_KEYWORDS)

    # ───────────── DELETE SPAM IF DETECTED ─────────────
    if is_text_spam or is_url_spam or is_keyword_spam:
        try:
            await msg.delete()
            logging.info(f"Deleted message from {msg.from_user.id}: {text}")
        except:
            logging.warning(f"Failed to delete message from {msg.from_user.id}")

        # ───────────── WARN / MUTE / BAN ─────────────
        if chat_id not in warnings:
            warnings[chat_id] = {}
        if user_id not in warnings[chat_id]:
            warnings[chat_id][user_id] = 0

        warnings[chat_id][user_id] += 1
        count = warnings[chat_id][user_id]

        if count == WARN_LIMIT:
            await msg.reply_text(f"⚠️ Warning {msg.from_user.first_name}, follow the rules!")
        elif count == MUTE_LIMIT:
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(msg.date.timestamp()) + MUTE_DURATION
            )
            await msg.reply_text(f"🔇 {msg.from_user.first_name} muted for {MUTE_DURATION//60} mins.")
        elif count >= BAN_LIMIT:
            await context.bot.ban_chat_member(chat_id, user_id)
            await msg.reply_text(f"⛔ {msg.from_user.first_name} banned for repeated spam.")
            warnings[chat_id].pop(user_id)

        # ───────────── UPSELL FOR NON-PREMIUM GROUPS ─────────────
        if not is_premium(chat_id):
            await upsell_after_delete(update, context)
