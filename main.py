import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
# তোমার Telegram ID এখানে বসাও। @userinfobot কে /start দিয়ে তোমার ID নাও
ADMIN_ID = 7834320405 # এটা তোমার ID দিয়ে চেঞ্জ করে দিও

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "No username"
    full_name = user.full_name

    # 1. ইউজারকে Pending মেসেজ দেওয়া
    user_text = f"""⏳ Start : পেন্ডিং

📮 Post : আপনার আইডি unactive কিভাবে একটিভ করবেন নিচে তার ভিডিও দেওয়া হলো 👇

🎬 ভিডিওর লিংক : https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7

📩 Telegram : @mahabul546
📞 WhatsApp : 0

👤 ইউজার নাম : {username}
🆔 ইউজার আইডি : {user_id}
"""
    await update.message.reply_text(user_text)

    # 2. তোমার কাছে Approve/Reject পাঠানো
    admin_text = f"""🔔 নতুন ইউজার Start দিয়েছে

👤 নাম : {full_name}
🔗 ইউজার নাম : {username}
🆔 ইউজার আইডি : `{user_id}`

কি করবে?"""

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        print(f"Admin send failed: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    target_id = data.split("_")[1]

    if data.startswith("approve_"):
        try:
            await context.bot.send_message(chat_id=target_id, text="✅ আপনার আইডি Active করে দেওয়া হয়েছে!")
            await query.edit_message_text(f"✅ {target_id} কে Approve করা হয়েছে।")
        except:
            await query.edit_message_text(f"⚠️ Approve করা হয়েছে কিন্তু ইউজারকে মেসেজ দেওয়া যায়নি: {target_id}")

    elif data.startswith("reject_"):
        try:
            await context.bot.send_message(chat_id=target_id, text="❌ আপনার আইডি Reject করা হয়েছে। @mahabul546 তে যোগাযোগ করুন।")
            await query.edit_message_text(f"❌ {target_id} কে Reject করা হয়েছে।")
        except:
            await query.edit_message_text(f"⚠️ Reject করা হয়েছে কিন্তু ইউজারকে মেসেজ দেওয়া যায়নি: {target_id}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
