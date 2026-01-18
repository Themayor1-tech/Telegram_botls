from telegram import Update
from telegram.ext import ContextTypes
from config import PREMIUM_PRICE

async def upsell_after_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    msg = (
        "🛡️ Safe Group AI\n\n"
        "Spam blocked successfully.\n\n"
        "Upgrade to Premium for:\n"
        "• Advanced spam detection\n"
        "• Auto mute & ban\n"
        "• Priority support\n\n"
        f"One-time fee: {PREMIUM_PRICE}"
    )

    await context.bot.send_message(chat_id=chat_id, text=msg)
