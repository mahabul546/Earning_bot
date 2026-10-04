import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7834320405

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""⏳ Start : পেন্ডিং

📮 Post : আপনার আইডি unactive কিভাবে একটিভ করবেন নিচে তার ভিডিও দেওয়া হলো 👇

📩 Telegram : @mahabul546
📞 WhatsApp : 0

👤 ইউজার নাম : @{user.username if user.username else user.first_name}
🆔 ইউজার আইডি : {user.id}
"""
    # লিংক এখন লেখায় নাই, শুধু বাটনে আছে - এটাই প্রাইভেট
    keyboard = [
        [InlineKeyboardButton("👉 Video 👈", url="https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

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
        await q.edit_message_text(f"✅ {uid} কে Approve করা হয়েছে!")
    else:
        await context.bot.send_message(chat_id=uid, text="❌ আপনার আইডি Reject করা হয়েছে!")
        await q.edit_message_text(f"❌ {uid} কে Reject করা হয়েছে!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.run_polling()
