<<<<<<< HEAD
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running perfectly!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot started...")
=======
import logging
import os
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, PREMIUM_PRICE
from moderation import moderate
from database import add_group, set_premium
from upsell import upsell_after_delete

# ───────────── AUTO CREATE LOGS FOLDER ─────────────
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename='logs/bot.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.info("Safe Group AI bot started.")

# ───────────── START COMMAND ─────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ Safe Group AI is active.\n\n"
        "➕ Add me to your group\n"
        "🛠 Make me admin\n"
        "⚡ Protection starts instantly"
    )

# ───────────── BOT ADDED TO GROUP ─────────────
async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            add_group(chat.id, int(time.time()))
            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    "🛡️ Safe Group AI Activated\n"
                    "This group is now under protection.\n"
                    "Spam, links, and scam messages will be blocked automatically."
                )
            )

# ───────────── ADMIN UPGRADE COMMAND ─────────────
async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    member = await context.bot.get_chat_member(chat_id, user.id)
    if member.status not in ["administrator", "creator"]:
        return

    set_premium(chat_id)

    await update.message.reply_text(
        f"🛡️ Safe Group AI Premium activated!\n"
        f"Advanced spam protection is now active.\n"
        f"One-time payment: {PREMIUM_PRICE}"
    )

# ───────────── MAIN ─────────────
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upgrade", upgrade))

    # Detect when bot is added to group
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bot_added))

    # Moderate messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderate))

    print("🛡️ Safe Group AI running...")
>>>>>>> 3c6e644 (Fixed spam deletion and improved moderation logic)
    app.run_polling()

if __name__ == "__main__":
    main()
