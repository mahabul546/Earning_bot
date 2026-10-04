import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7834320405
DATA_FILE = "data.json"

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

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # --- শুধু রেফার এর জন্য এইটুকু Add করলাম ---
    data = load_data()
    args = context.args
    if args and args[0]!= str(user.id):
        ref_id = args[0]
        if str(user.id) not in data:
            data[str(user.id)] = {"balance": 0, "referrals": [], "withdraw_ref": 0, "referred_by": ref_id}
            if ref_id in data:
                if str(user.id) not in data[ref_id]["referrals"]:
                    data[ref_id]["referrals"].append(str(user.id))
                    data[ref_id]["balance"] += 20
            else:
                data[ref_id] = {"balance": 20, "referrals": [str(user.id)], "withdraw_ref": 0, "referred_by": None}
            save_data(data)
    # --- শেষ ---

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
    text = update.message.text
    user_id = str(update.effective_user.id)

    # --- শুধু My Referrals এর জন্য ---
    if text == "👥 My Referrals":
        data = load_data()
        if user_id not in data:
            data[user_id] = {"balance": 0, "referrals": [], "withdraw_ref": 0, "referred_by": None}
            save_data(data)
        d = data[user_id]
        total_ref = len(d.get("referrals", []))
        withdraw_ref = d.get("withdraw_ref", 0)
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"

        msg = f"""💸 রেফার করে অটোমেটিক ইনকাম করুন!

💲 প্রতি রেফার ২০ টাকা করে পাবেন

👥 Total Referral: {total_ref}

💵 Withdraw Referral: {withdraw_ref}

🔗 Your Referral Link:
{ref_link}

⚠️ রেফার করা ইউজার withdraw করলে
Withdraw Referral বাড়বে।

🔙 Back to menu"""
        await update.message.reply_text(msg)
        return

    # আগের মতোই থাকবে
    await update.message.reply_text(f"আপনি ক্লিক করেছেন: {update.message.text}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.run_polling()
