import os, json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7834320405
ADMINS = [ADMIN_ID]
DATA_FILE = "data.json"
REQUIRED_CHANNEL = "@mhabul546"

USER_MENU = [["👥 My Referrals", "🎯 Tasks"], ["💰 Balance", "📢 Notice"], ["💬 Support", "👤 My accounts"]]
ADMIN_MENU = [["👥 My Referrals", "🎯 Tasks"], ["💰 Balance", "📢 Notice"], ["💬 Support", "👤 My accounts"], ["⚙️ Admin Panel"]]

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
        json.dump(data, f, indent=2)
    try:
        os.system('git config --global user.email "bot@auto.com" > /dev/null 2>&1')
        os.system('git config --global user.name "auto-bot" > /dev/null 2>&1')
        os.system(f'git add {DATA_FILE} > /dev/null 2>&1')
        os.system('git diff --cached --quiet || git commit -m "auto save data.json [skip ci]" > /dev/null 2>&1')
        os.system('git push > /dev/null 2>&1 || true')
    except:
        pass

def get_user(data, uid, effective_user=None):
    uid=str(uid)
    if uid not in data:
        data[uid]={"balance":0, "referrals":[], "withdraw_ref":0, "referred_by":None, "history":[], "first_name": "N/A", "username": "N/A", "full_name": "N/A"}
    if "history" not in data[uid]: data[uid]["history"]=[]
    if "first_name" not in data[uid]: data[uid]["first_name"]="N/A"
    if effective_user:
        data[uid]["first_name"] = effective_user.first_name
        data[uid]["username"] = f"@{effective_user.username}" if effective_user.username else "N/A"
        data[uid]["full_name"] = effective_user.full_name
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
        u = get_user(data, user.id, user)
        if not u["referred_by"]:
            u["referred_by"]=ref_id
            r = get_user(data, ref_id)
            if str(user.id) not in r["referrals"]:
                r["referrals"].append(str(user.id))
            save_data(data)
    else:
        get_user(data, user.id, user)
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
        await update.message.reply_text("Select an action from the menu list 👇", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))
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
        u = get_user(data, uid)
        save_data(data)
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
    text = update.message.text.strip() if update.message.text else ""
    uid = str(update.effective_user.id)
    data = load_data()
    u = get_user(data, uid, update.effective_user)
    save_data(data)

    if text == "🔙 Back":
        context.user_data.clear()
        main = ADMIN_MENU if int(uid)==ADMIN_ID else USER_MENU
        await update.message.reply_text("Select an action from the menu list 👇", reply_markup=ReplyKeyboardMarkup(main, resize_keyboard=True))
        return

    admin_action = context.user_data.get("admin_action")
    admin_buttons = ["👥 Total Users", "📊 Stats", "💳 Withdraw Requests", "🔍 Search Pending", "💰 Balance Add", "💰 Balance Remove", "🚫 Block / Unblock", "📢 Broadcast", "⚙️ Admin Panel"]
    if text in admin_buttons and text not in ["💰 Balance Add", "💰 Balance Remove"]:
        context.user_data["admin_action"] = None
        admin_action = None

    # ====== নতুন ২টা - আগের কিছু ডিলিট হয়নি ======
    if text == "👥 Total Users":
        if int(uid) not in ADMINS: return
        total = len([k for k in data.keys() if k.isdigit()])
        msg = f"👥 Total Users: {total} জন\n\n"
        for k,v in list(data.items())[-20:]:
            if not k.isdigit(): continue
            msg += f"{v.get('first_name','N/A')} - {k} - {v.get('balance',0)}৳\n"
        await update.message.reply_text(msg)
        return

    if text == "📊 Stats":
        if int(uid) not in ADMINS: return
        total_users = len([k for k in data.keys() if k.isdigit()])
        total_bal = sum(v.get('balance',0) for v in data.values())
        total_ref = sum(len(v.get('referrals',[])) for v in data.values())
        pending_c = 0
        pending_t = 0
        for v in data.values():
            for h in v.get('history',[]):
                if h.get('status')=="PENDING":
                    pending_c+=1
                    pending_t+=h.get('amount',0)
        msg = f"📊 STATS\n\n👥 Total Users: {total_users}\n💰 Total Balance: {total_bal}৳\n👥 Total Referral: {total_ref}\n⏳ Pending: {pending_c} টা ({pending_t}৳)"
        await update.message.reply_text(msg)
        return
    # ====== নতুন ২টা শেষ ======

    if text == "💳 Withdraw Requests":
        if int(uid) not in ADMINS: return
        data = load_data()
        pending_list = []
        for user_id, udata in data.items():
            if not user_id.isdigit(): continue
            for h in udata.get("history", []):
                if h.get("status") == "PENDING":
                    pending_list.append((user_id, udata.get("first_name","N/A"), h))
        
        if not pending_list:
            await update.message.reply_text("✅ কোনো Pending Withdraw নেই")
            return

        msg = f"💳 PENDING WITHDRAW: {len(pending_list)} টা\n\n"
        kb_buttons = []
        for user_id, name, h in pending_list[:15]: # প্রথম 15 টা দেখাবে, বেশি হলে লোড বেশি হবে
            msg += f"👤 {name} | {user_id}\n💰 {h['amount']}৳ | {h['method']} | {h['number']}\n🆔 WID: {h['id']} | {h['date']}\n\n"
            kb_buttons.append([InlineKeyboardButton(f"✅ PAID {h['amount']}৳ - {user_id}", callback_data=f"withdraw_paid_{user_id}_{h['id']}")])
        
        if len(pending_list) > 15:
            msg += f"...আরও {len(pending_list)-15} টা Pending আছে"

        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb_buttons))
        return

    if text == "🔍 Search Pending":
        if int(uid) not in ADMINS: return
        context.user_data["admin_action"] = "search_pending"
        await update.message.reply_text("🔍 যে ইউজারের Pending দেখতে চাও তার User ID দাও:")
        return

    if admin_action == "search_pending":
        target_id = text.strip()
        target = data.get(target_id)
        if not target:
            await update.message.reply_text(f"❌ এই ID পাওয়া যায়নি: {target_id}")
            return
        
        pending = [h for h in target.get("history", []) if h.get("status")=="PENDING"]
        if not pending:
            await update.message.reply_text(f"✅ {target_id} এর কোনো Pending নেই\nName: {target.get('first_name','N/A')}\nBalance: {target.get('balance',0)}৳")
            context.user_data["admin_action"] = None
            return

        msg = f"🔍 Pending for {target_id}\n👤 {target.get('first_name','N/A')}\n💰 Balance: {target.get('balance',0)}৳\n\n"
        kb_buttons = []
        for h in pending:
            msg += f"💰 {h['amount']}৳ | {h['method']} | {h['number']}\n🆔 {h['id']} | {h['date']}\n\n"
            kb_buttons.append([InlineKeyboardButton(f"✅ PAID {h['amount']}৳", callback_data=f"withdraw_paid_{target_id}_{h['id']}")])

        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb_buttons))
        context.user_data["admin_action"] = None
        return
          # ====== নতুন ২টা শেষ ======
    
    
    if admin_action == "find_user_for_balance":
        target = data.get(text)
        if not target:
            if not text.isdigit():
                await update.message.reply_text(f"❌ ভুল ID! শুধু নাম্বার দিন\nতুমি দিয়েছো: {text}")
                return
            target = get_user(data, text)
            save_data(data)
            await update.message.reply_text(f"⚠️ এই ID আগে ছিল না, নতুন তৈরি করা হলো!\nID: {text}\nএখন + - দিন:")
            context.user_data["edit_target_id"] = text
            context.user_data["admin_action"] = "edit_balance_amount"
            return
        context.user_data["edit_target_id"] = text
        context.user_data["admin_action"] = "edit_balance_amount"
        bal = target.get('balance', 0)
        name = target.get('first_name', 'N/A')
        msg = f"👤 User Found!\n\n📛 Name: {name}\n🆔 ID: {text}\n💰 Balance: {bal}৳\n\n+100 লিখলে যোগ হবে\n-50 লিখলে কাটবে\nEx: +100"
        await update.message.reply_text(msg)
        return

    if admin_action == "edit_balance_amount":
        try:
            target_id = context.user_data.get("edit_target_id")
            target = get_user(data, target_id)
            amount = int(text)
            target["balance"] += amount
            if target["balance"] < 0:
                target["balance"] = 0
            save_data(data)
            await update.message.reply_text(f"✅ Done! ID: {target_id}\n💰 {amount}৳ | Now: {target['balance']}৳\n\nআবার ID দিন বা 🔙 Back চাপুন")
            context.user_data["admin_action"] = "find_user_for_balance"
        except:
            await update.message.reply_text("❌ ভুল! +100 বা -50 লিখুন")
        return

    if text == "💸 Payout":
        joined = await check_joined(context.bot, update.effective_user.id)
        if not joined:
            kb = [[InlineKeyboardButton("📱 Join Channel", url="https://t.me/mhabul546")],[InlineKeyboardButton("▶️ YouTube Subscribe", url="https://youtube.com/@mahabul546?si=Vy6Zhd1l1P8jeNfJ")],[InlineKeyboardButton("✅ I Joined - Check", callback_data="check_join")]]
            await update.message.reply_text("❌ পেমেন্ট নিতে হলে আগে চ্যানেলে জয়েন করুন!", reply_markup=InlineKeyboardMarkup(kb))
            return
        if u["balance"] < 50:
            await update.message.reply_text(f"❌ আপনার ব্যালেন্স {u['balance']} টাকা, মিনিমাম 50 টাকা লাগবে!")
            return
        context.user_data.clear()
        kb = ReplyKeyboardMarkup([["Bikas"],["Nogod"],["Rocket"],["🔙 Back"]], resize_keyboard=True)
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
        kb = ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True)
        await update.message.reply_text(f"আপনি {text} সিলেক্ট করেছেন। এখন আপনার {text} নাম্বার দিন:", reply_markup=kb)
        return

    if context.user_data.get("step") == "number":
        if not text.isdigit() or len(text) != 11 or not text.startswith("01"):
            await update.message.reply_text("❌ ভুল নাম্বার! সঠিক 11 ডিজিটের নাম্বার দিন\nযেমন: 01712345678")
            return
        context.user_data["number"]=text
        context.user_data["step"]="amount"
        await update.message.reply_text("✅ নাম্বার ঠিক আছে। এখন কত টাকা উইথড্র করবেন লিখুন (মিনিমাম 50):")
        return

    if context.user_data.get("step") == "amount":
        try: amount = int(text)
        except:
            await update.message.reply_text("❌ সঠিক সংখ্যা লিখুন! যেমন: 100")
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
        joined = await check_joined(context.bot, update.effective_user.id)
        if not joined:
            kb = [[InlineKeyboardButton("📱 Join Channel", url="https://t.me/mhabul546")],[InlineKeyboardButton("▶️ YouTube Subscribe", url="https://youtube.com/@mahabul546?si=Vy6Zhd1l1P8jeNfJ")],[InlineKeyboardButton("✅ I Joined - Check", callback_data="check_join")]]
            await update.message.reply_text("❌ পেমেন্ট পেতে হলে আগে আমাদের চ্যানেলে জয়েন করতে হবে!\n\nজয়েন করে Check বাটনে চাপ দিন।", reply_markup=InlineKeyboardMarkup(kb))
            return
        bal = u["balance"]
        msg = f"""বিঃদ্রঃ উইথড্র দেওয়া 2 ঘণ্টার মধ্যে পেমেন্ট দেয়া হবে
আপনার ব্যালেন্স💰 : {bal} টাকা
মিনিম্যাম উইথড্র 50 টাকা"""
        kb = ReplyKeyboardMarkup([["💸 Payout", "📜 Balance History"], ["🔙 Back"]], resize_keyboard=True)
        await update.message.reply_text(msg, reply_markup=kb)
        return

    if text == "💬 Support":
        msg = ("🆘 Support Center\n\nযেকোনো সমস্যায় আমাদের সাপোর্টে যোগাযোগ করুন। 💬\n\n📱 WhatsApp: https://wa.me/8801980448738\n📲 Telegram: @myearn546\n\n দ্রুত সহায়তার জন্য সমস্যাটি বিস্তারিত জানান।")
        await update.message.reply_text(msg)
        return

    if text == "👤 My accounts":
        user = update.effective_user
        msg = (f"👤 MY ACCOUNT\n\n🆔 ID: {user.id}\n👤 Name: {user.first_name}\n📅 Joined: {u.get('joined_date', 'N/A')}\n")
        await update.message.reply_text(msg)
        return

    if text == "⚙️ Admin Panel":
        if update.effective_user.id not in ADMINS:
            return
        kb = [["👥 Total Users", "📊 Stats"],["💳 Withdraw Requests", "🔍 Search Pending"],["💰 Balance Add", "💰 Balance Remove"],["🚫 Block / Unblock", "📢 Broadcast"],["🔙 Back"]]
        await update.message.reply_text("⚙️ ADMIN PANEL", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        return

    if text == "💰 Balance Add" or text == "💰 Balance Remove":
        if update.effective_user.id not in ADMINS:
            return
        context.user_data["admin_action"] = "find_user_for_balance"
        await update.message.reply_text("💰 ব্যালেন্স এডিট করতে User ID দিন:")
        return
    
    if text == "📜 Balance History":
        pending = sum([h["amount"] for h in u["history"] if h["status"]=="PENDING"])
        total_times = len(u["history"])
        msg = f"📜 BALANCE HISTORY\n\n⏳ পেন্ডিং ব্যালেন্স: {pending} টাকা\n🔄 মোট উইথড্র: {total_times} বার\n\n📜 উইথড্র হিস্টরি:\n"
        if not u["history"]:
            msg += "কোনো হিস্টরি নেই"
        else:
            for i, h in enumerate(reversed(u["history"][-10:]), 1):
                msg += f"{i}. {h['amount']}৳ - {h['status']}\n📱 {h['method']} : {h['number']}\n {h['date']}\n\n"
        await update.message.reply_text(msg)
        return

    if text == "🎯 Tasks":
        kb = ReplyKeyboardMarkup([["📧 Gmail sell", "💬 Whatsapp sell"],["🎥 Videos earn", "▶️ YouTube"],["💳 Recharge", "🌐 Website visit"],["🔙 Back"]], resize_keyboard=True)
        await update.message.reply_text("🎯 টাস্ক সিলেক্ট করুন 👇", reply_markup=kb)
        return

    if text == "📧 Gmail sell":
        msg = """ সম্পূর্ণ পদ্ধতি জানতে ভিডিওটি দেখুন ⬇️
💳 কিভাবে সহজে Withdraw করে bKash / Nagad / Rocket-এ টাকা পাবেন
ধাপে ধাপে জানতে ভিডিওটি দেখুন ⬇️
💰 মাত্র ৩ টা Gmail = ৬৩ টাকা ইনকাম
➡️ মিনিমাম : 0.60 সেন্ট = ৫৫ টাকা
🧢 Ther (vsjdbsj): <code>0x35a886358182eb30396ed3e6a4334e4bf582e33c</code>
কিভাবে বেশি দামে বিক্রি করবেন তার ভিডিও নিচে দেওয়া হলো"""
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 Income Video", url="https://youtu.be/1FQIGuWkw5A?si=eP_aWUEZbGfzlcMC")],[InlineKeyboardButton("🔗 Registration", url="https://youtu.be/uOS30DdJW74?si=Koe_Ueww8ByhxA6-")],[InlineKeyboardButton("💳 Withdraw Video", url="https://youtu.be/TBNw7WSaYoo?si=tLDRjNWw5HMu3xwu")],[InlineKeyboardButton("👨‍👨‍👦 Sell to Sell 👨‍👨‍👦", url="https://t.me/Mahabul545erningbot")]])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
        return

    if text in [ "💬 Whatsapp sell", "🎥 Videos earn", "▶️ YouTube", "💳 Recharge", "🌐 Website visit"]:
        await update.message.reply_text(f"🔧 {text} - কাজ চলছে, খুব শীঘ্রই আপডেট আসবে!")
        return

    if text == "👥 My Referrals":
        total_ref = len(u.get("referrals", []))
        withdraw_ref = u.get("withdraw_ref", 0)
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={uid}"
        msg = f"""💸 রেফার করে অটোমেটিক ইনকাম করুন!
💲 প্রতি রেফার ২০ টাকা করে পাবেন paben
👥 Total Referral: {total_ref}
💵 Withdraw Referral: {withdraw_ref}
🔗 Your Referral Link:
{ref_link}
⚠️ রেফার করা ইউজার withdraw করলে Withdraw Referral বাড়বে।"""
        await update.message.reply_text(msg)
        return

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.run_polling()
