import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7834320405

USER_MENU = [
    ["👥 My Referrals", "🎯 Tasks"],
    ["💰 Balance", "📢 Notice"],
    ["💬 Support"]
]
ADMIN_MENU = [
    ["👥 My Referrals", "🎯 Tasks"],
    ["💰 Balance", "📢 Notice"],
    ["💬 Support", "⚙️ Admin Panel"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""⏳ Start : পেন্ডিং

📮 Post : আপনার আইডি unactive কিভাবে একটিভ করবেন নিচে তার ভিডিও দেওয়া হলো 👇

📩 Telegram : @mahabul546
📞 WhatsApp : 0

👤 ইউজার নাম : @{user.username if user.username else user.first_name}
🆔 ইউজার আইডি : {user.id}
"""
    keyboard = [[InlineKeyboardButton("👉 Video 👈", url="https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

    if user.id == ADMIN_ID:
        main_menu = ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True)
        await update.message.reply_text("নিচ থেকে সিলেক্ট করুন 👇", reply_markup=main_menu)

    admin_text = f"🔔 New User\nName: {user.full_name}\nUsername: @{user.username}\nID: {user.id}"
    kb = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
    try:
        await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=InlineKeyboardMarkup(kb))
    except: pass

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.data.split("_")[1]
    if "approve" in q.data:
        kb = [[InlineKeyboardButton("👉 Video 👈", url="https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7")]]
        await context.bot.send_message(chat_id=uid, text="✅ আপনার আইডি Active করা হয়েছে!", reply_markup=InlineKeyboardMarkup(kb))

        if int(uid) == ADMIN_ID:
            main_menu = ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True)
        else:
            main_menu = ReplyKeyboardMarkup(USER_MENU, resize_keyboard=True)
        await context.bot.send_message(chat_id=uid, text="নিচ থেকে সিলেক্ট করুন 👇", reply_markup=main_menu)

        await q.edit_message_text(f"✅ {uid} কে Approve করা হয়েছে!")
    else:
        await context.bot.send_message(chat_id=uid, text="❌ আপনার আইডি Reject করা হয়েছে!")
        await q.edit_message_text(f"❌ {uid} কে Reject করা হয়েছে!")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"আপনি ক্লিক করেছেন: {update.message.text}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.run_polling()
