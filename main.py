import os, json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7834320405
DATA_FILE = "data.json"
REQUIRED_CHANNEL = "@mhabul546"

USER_MENU = [["👥 My Referrals", "🎯 Tasks"], ["💰 Balance", "📢 Notice"], ["💬 Support", "👤 My accounts"]]
ADMIN_MENU = [["👥 My Referrals", "🎯 Tasks"], ["💰 Balance", "📢 Notice"], ["💬 Support", "👤 My accounts"], ["⚙️ Admin Panel"]]

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def get_user(data, uid):
    uid=str(uid)
    if uid not in data:
        data[uid]={"balance":0, "referrals":[], "withdraw_ref":0, "referred_by":None, "history":[]}
    if "history" not in data[uid]: data[uid]["history"]=[]
    return data[uid]

async def check_joined(bot, user_id):
    try:
        m = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator", "owner"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    args = context.args
    if args and args[0]!= str(user.id):
        ref_id = args[0]
        u = get_user(data, user.id)
        if not u["referred_by"]:
            u["referred_by"]=ref_id
            r = get_user(data, ref_id)
            if str(user.id) not in r["referrals"]:
                r["referrals"].append(str(user.id))
            save_data(data)

    text = f"""⏳ Start : পেন্ডিং
📮 Post : আপনার আইডি unactive কিভাবে একটিভ করবেন নিচে তার ভিডিও দেওয়া হলো 👇
📩 Telegram : @mahabul546
📞 WhatsApp : 0
👤 ইউজার নাম : @{user.username if user.username else user.first_name}
🆔 ইউজার আইডি : {user.id}"""
    keyboard = [[InlineKeyboardButton("👉 Video 👈", url="https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
    if user.id == ADMIN_ID:
        await update.message.reply_text("নিচ থেকে সিলেক্ট করুন 👇", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))
    admin_text = f"🔔 New User\nName: {user.full_name}\nUsername: @{user.username}\nID: {user.id}"
    kb = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
    try: await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=InlineKeyboardMarkup(kb))
    except: pass

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = load_data()

    if q.data == "check_join":
        joined = await check_joined(context.bot, q.from_user.id)
        if joined:
            await q.edit_message_text("✅ ধন্যবাদ! আপনি জয়েন করেছেন। এখন /start দিয়ে Balance এ যান।")
        else:
            await q.answer("❌ এখনো জয়েন করেন নাই!", show_alert=True)
        return

    if "withdraw_paid_" in q.data:
        wid = q.data.split("_")[-1]
        uid = q.data.split("_")[-2]
        u = get_user(data, uid)
        for h in u["history"]:
            if str(h["id"]) == wid:
                h["status"]="PAID"
                save_data(data)
                await context.bot.send_message(uid, f"✅ আপনার {h['amount']}৳ পেমেন্ট PAID করা হয়েছে!")
                await q.edit_message_text(f"✅ {uid} এর {wid} PAID করা হলো")
                return

    if "approve_" in q.data or "reject_" in q.data:
        uid = q.data.split("_")[1]
        if "approve" in q.data:
            kb = [[InlineKeyboardButton("👉 Video 👈", url="https://youtube.com/shorts/q7sZG9w9PhA?si=LYnMkkFQcwt32Mm7")]]
            await context.bot.send_message(chat_id=uid, text="✅ আপনার আইডি Active করা হয়েছে!", reply_markup=InlineKeyboardMarkup(kb))
            main = ReplyKeyboardMarkup(ADMIN_MENU if int(uid)==ADMIN_ID else USER_MENU, resize_keyboard=True)
            await context.bot.send_message(chat_id=uid, text="নিচ থেকে সিলেক্ট করুন 👇", reply_markup=main)
            await q.edit_message_text(f"✅ {uid} কে Approve করা হয়েছে!")
        else:
            await context.bot.send_message(chat_id=uid, text="❌ আপনার আইডি Reject করা হয়েছে!")
            await q.edit_message_text(f"❌ {uid} কে Reject করা হয়েছে!")
        return

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()
    u = get_user(data, uid)

    if context.user_data.get("step") == "number":
        context.user_data["number"]=text
        context.user_data["step"]="amount"
        await update.message.reply_text("এখন কত টাকা উইথড্র করবেন লিখুন (মিনিমাম 50):")
        return
    if context.user_data.get("step") == "amount":
        try: amount = int(text)
        except:
            await update.message.reply_text("❌ সঠিক সংখ্যা লিখুন!")
            return
        if amount < 50:
            await update.message.reply_text("❌ 50 টাকার নিচে উইথড্র করা যাবে না!")
            return
        if amount > u["balance"]:
            await update.message.reply_text(f"❌ আপনার ব্যালেন্সে {u['balance']} টাকা আছে, এর বেশি পারবেন না!")
            return
        method = context.user_data["method"]
        number = context.user_data["number"]
        u["balance"] -= amount
        wid = int(datetime.now().timestamp())
        entry = {"id": wid, "amount": amount, "method": method, "number": number, "status": "PENDING", "date": datetime.now().strftime("%d/%m/%Y | %I:%M %p")}
        u["history"].append(entry)
        ref_id = u.get("referred_by")
        if ref_id:
            ref_user = get_user(data, ref_id)
            ref_user["balance"] += 20
            ref_user["withdraw_ref"] = ref_user.get("withdraw_ref",0)+1
            try:
                await context.bot.send_message(ref_id, f"🎉 আপনি 20 টাকা রেফার বোনাস পেয়েছেন! {uid} উইথড্র করেছে।")
                await context.bot.send_message(ADMIN_ID, f"🔔 {ref_id} ইউজার 20 টাকা বোনাস পেয়েছে, রেফার {uid} উইথড্র করেছে")
            except: pass
        save_data(data)
        context.user_data.clear()
        await update.message.reply_text(f"✅ {amount}৳ উইথড্র রিকোয়েস্ট পাঠানো হয়েছে!\n{method}: {number}\n\nটাকা আপনার ব্যালেন্স থেকে কেটে নেওয়া হয়েছে।")
        kb = [[InlineKeyboardButton("✅ PAID", callback_data=f"withdraw_paid_{uid}_{wid}")]]
        try:
            await context.bot.send_message(ADMIN_ID, f"💸 New Withdraw\nUser: {uid}\nAmount: {amount}\nMethod: {method}\nNumber: {number}\nID: {wid}", reply_markup=InlineKeyboardMarkup(kb))
        except: pass
        return

    if text == "📢 Notice":
        msg = """পেমেন্ট পাওয়ার নিয়ম
পেমেন্ট পেতে হলে নিচের ২টি চ্যানেলেই জয়েন/সাবস্ক্রাইব করা বাধ্যতামূলক 👇
📱 Telegram Channel: https://t.me/mhabul546
▶️ YouTube Channel: https://youtube.com/@mahabul546?si=Vy6Zhd1l1P8jeNfJ
⚠️ গুরুত্বপূর্ণ: উপরের যেকোনো একটি চ্যানেলে জয়েন/সাবস্ক্রাইব না থাকলে পেমেন্ট দেওয়া হবে না।"""
        kb = [[InlineKeyboardButton("📱 Telegram Join", url="https://t.me/mhabul546")],[InlineKeyboardButton("▶️ YouTube Subscribe", url="https://youtube.com/@mahabul546?si=Vy6Zhd1l1P8jeNfJ")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        return

    if text == "💰 Balance":
        # === জয়েন চেক এখানে ===
        joined = await check_joined(context.bot, update.effective_user.id)
        if not joined:
            kb = [[InlineKeyboardButton("📱 Join Channel", url="https://t.me/mhabul546")],[InlineKeyboardButton("✅ I Joined - Check", callback_data="check_join")]]
            await update.message.reply_text("❌ পেমেন্ট পেতে হলে আগে আমাদের চ্যানেলে জয়েন করতে হবে!\n\nজয়েন করে Check বাটনে চাপ দিন।", reply_markup=InlineKeyboardMarkup(kb))
            return
        # জয়েন থাকলে ব্যালেন্স দেখাবে
        bal = u["balance"]
        msg = f"""বিঃদ্রঃ উইথড্র দেওয়া 2 ঘণ্টার মধ্যে পেমেন্ট দেয়া হবে

আপনার ব্যালেন্স💰 : {bal} টাকা

মিনিম্যাম উইথড্র 50 টাকা"""
        kb = ReplyKeyboardMarkup([["💸 Payout", "📜 Balance History"], ["🔙 Back"]], resize_keyboard=True)
        await update.message.reply_text(msg, reply_markup=kb)
        return

    if text == "💸 Payout":
        joined = await check_joined(context.bot, update.effective_user.id)
        if not joined:
            kb = [[InlineKeyboardButton("📱 Join Channel", url="https://t.me/mhabul546")],[InlineKeyboardButton("✅ I Joined - Check", callback_data="check_join")]]
            await update.message.reply_text("❌ পেমেন্ট নিতে হলে আগে চ্যানেলে জয়েন করুন!", reply_markup=InlineKeyboardMarkup(kb))
            return
        if u["balance"] < 50:
            await update.message.reply_text(f"❌ আপনার ব্যালেন্স {u['balance']} টাকা, মিনিমাম 50 টাকা লাগবে!")
            return
        kb = ReplyKeyboardMarkup([["Bikas", "Nogod", "Rocket"], ["🔙 Back"]], resize_keyboard=True)
        await update.message.reply_text("পেমেন্ট মেথড সিলেক্ট করুন:", reply_markup=kb)
        return

    if text in ["Bikas", "Nogod", "Rocket"]:
        joined = await check_joined(context.bot, update.effective_user.id)
        if not joined:
            await update.message.reply_text("❌ আগে চ্যানেলে জয়েন করুন!")
            return
        if u["balance"] < 50:
            await update.message.reply_text("❌ 50 টাকার নিচে উইথড্র হবে না!")
            return
        context.user_data["method"]=text
        context.user_data["step"]="number"
        await update.message.reply_text(f"আপনি {text} সিলেক্ট করেছেন। এখন আপনার {text} নাম্বার দিন:")
        return
নতুন বসাইছি এখন থেকে 
if text == "💬 Support":
        msg = (
            "🆘 Support Center\n\n"
            "যেকোনো সমস্যায় আমাদের সাপোর্টে যোগাযোগ করুন। 💬\n\n"
            "📱 WhatsApp: https://wa.me/8801980448738\n"
            "📲 Telegram: @myearn546\n\n"
            "⚡ দ্রুত সহায়তার জন্য সমস্যাটি বিস্তারিত জানান।"
        )
    এখন পর্যন্ত 

    if text == "📜 Balance History":
        pending = sum([h["amount"] for h in u["history"] if h["status"]=="PENDING"])
        total_times = len(u["history"])
        msg = f"📜 BALANCE HISTORY\n\n⏳ পেন্ডিং ব্যালেন্স: {pending} টাকা\n🔄 মোট উইথড্র: {total_times} বার\n\n📜 উইথড্র হিস্টরি:\n"
        if not u["history"]:
            msg += "কোনো হিস্টরি নেই"
        else:
            for i, h in enumerate(reversed(u["history"][-10:]), 1):
                msg += f"{i}. {h['amount']}৳ - {h['status']}\n📱 {h['method']} : {h['number']}\n📅 {h['date']}\n\n"
        await update.message.reply_text(msg)
        return
  
    if text == "🎯 Tasks":
        kb = ReplyKeyboardMarkup([
            ["📧 Gmail sell", "💬 Whatsapp sell"],
            ["🎥 Videos earn", "▶️ YouTube"],
            ["💳 Recharge", "🌐 Website visit"],
            ["🔙 Back"]
        ], resize_keyboard=True)
        await update.message.reply_text("🎯 টাস্ক সিলেক্ট করুন 👇", reply_markup=kb)
        return

    if text in ["📧 Gmail sell", "💬 Whatsapp sell", "🎥 Videos earn", "▶️ YouTube", "💳 Recharge", "🌐 Website visit"]:
        await update.message.reply_text(f"🔧 {text} - কাজ চলছে, খুব শীঘ্রই আপডেট আসবে!")
        return
        
    if text == "👥 My Referrals":
        total_ref = len(u.get("referrals", []))
        withdraw_ref = u.get("withdraw_ref", 0)
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={uid}"
        msg = f"""💸 রেফার করে অটোমেটিক ইনকাম করুন!
💲 প্রতি রেফার ২০ টাকা করে পাবেন
👥 Total Referral: {total_ref}
💵 Withdraw Referral: {withdraw_ref}
🔗 Your Referral Link:\n{ref_link}
⚠️ রেফার করা ইউজার withdraw করলে Withdraw Referral বাড়বে।"""
        await update.message.reply_text(msg)
        return

    if text == "🔙 Back":
        await update.message.reply_text("নিচ থেকে সিলেক্ট করুন 👇", reply_markup=ReplyKeyboardMarkup(USER_MENU if int(uid)!=ADMIN_ID else ADMIN_MENU, resize_keyboard=True))
        return

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.run_polling()
