import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7834320405

# ইউজারের মেইন মেনু
def get_main_menu(user_id):
    buttons = [
        ["Referral", "Allwork"],
        ["Balance", "Notice"],
        ["Support"]
    ]
    # Admin Panel শুধু এডমিন দেখবে
    if user_id == ADMIN_ID:
        buttons.append(["Admin Panel"])

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""⏳ Start : পেন্ডিং

📮 Post : আপনার আইডি unactive কিভাবে একটিভ করবেন নিচে তার ভিডিও দেওয়া হলো 👇

🎬 ভিডিওর লিংক : https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7

📩 Telegram : @mahabul546
📞 WhatsApp : 0

👤 ইউজার নাম : @{user.username if user.username else user.first_name}
🆔 ইউজার আইডি : {user.id}
"""
    await update.message.reply_text(text)

    admin_text = f"🔔 New User\nName: {user.full_name}\nUsername: @{user.username}\nID: {user.id}"
    kb = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
    try:
        await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=InlineKeyboardMarkup(kb))
    except: pass

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = int(q.data.split("_")[1])
    if "approve" in q.data:
        await context.bot.send_message(chat_id=uid, text="""✅ আপনার আইডি Active করা হয়েছে!

কিভাবে bot এ কাজ করবেন তার ভিডিও নিচে দেওয়া হলো 👇

https://youtube.com/shorts/IpF6C6kCxE4?si=dDLQaFihkH9UnYz0""", reply_markup=get_main_menu(uid))
        await q.edit_message_text(f"✅ {uid} কে Approve করা হয়েছে।")
    else:
        await context.bot.send_message(chat_id=uid, text="❌ আপনার আইডি Reject করা হয়েছে।")
        await q.edit_message_text(f"❌ {uid} কে Reject করা হয়েছে।")

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "Referral":
        await update.message.reply_text("🔗 আপনার রেফার লিংক: https://t.me/YourBot?start={}".format(user_id))
    elif text == "Allwork":
        await update.message.reply_text("📋 All Work List এখানে আসবে।")
    elif text == "Balance":
        await update.message.reply_text("💰 আপনার ব্যালেন্স: 0 টাকা")
    elif text == "Notice":
        await update.message.reply_text("📢 Notice: বট আপডেট করা হয়েছে।")
    elif text == "Support":
        await update.message.reply_text("📩 Support: @mahabul546")
    elif text == "Admin Panel":
        if user_id == ADMIN_ID:
            await update.message.reply_text("👑 Admin Panel এ স্বাগতম!\n\nএখানে সব ইউজার কন্ট্রোল করতে পারবেন।")
        else:
            await update.message.reply_text("❌ এই বাটন শুধু এডমিনের জন্য।")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.run_polling()
