import os
import json
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")

# এখানে তোমার নিজের Telegram User ID বসাবে
ADMIN_ID = 7834320405

bot = telebot.TeleBot(BOT_TOKEN)

USERS_FILE = "users.json"


# =========================
# USER DATABASE
# =========================

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)


# =========================
# MAIN MENU
# =========================

def main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "👥 Referral",
        " task"
    )

    keyboard.row(
        "💰 Balance",
        "📢 Notice"
    )

    keyboard.row(
        "🆘 Support"
    )

    return keyboard


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = str(message.from_user.id)
    name = message.from_user.first_name or "Unknown"
    username = message.from_user.username

    users = load_users()

    # =========================
    # APPROVED USER
    # =========================

    if user_id in users and users[user_id]["status"] == "approved":

        bot.send_message(
            message.chat.id,
            "✅ আপনার Account Approved আছে।\n\n"
            "স্বাগতম!",
            reply_markup=main_menu()
        )

        return

    # =========================
    # ALREADY PENDING
    # =========================

    if user_id in users and users[user_id]["status"] == "pending":

        bot.send_message(
            message.chat.id,
            "⏳ Pending Request\n\n"
            "একটু অপেক্ষা করুন। Admin ফ্রি হলে "
            "আপনার Request Approve করবেন।\n\n"
            f"👤 নাম: {name}\n"
            f"🆔 User ID: {message.from_user.id}"
        )

        return

    # =========================
    # NEW USER
    # =========================

    users[user_id] = {
        "id": message.from_user.id,
        "name": name,
        "username": username or "",
        "status": "pending"
    }

    save_users(users)

    # =========================
    # MEMBER MESSAGE
    # =========================

    pending_text = (
        "⏳ Pending Request\n\n"
        "একটু অপেক্ষা করুন। Admin ফ্রি হলে "
        "আপনার Request Approve করবেন।\n\n"
        f"👤 নাম: {name}\n"
        f"🆔 User ID: {message.from_user.id}"
    )

    sent_message = bot.send_message(
        message.chat.id,
        pending_text
    )

    # Pending message ID সংরক্ষণ
    users[user_id]["pending_message_id"] = sent_message.message_id
    save_users(users)

    # =========================
    # ADMIN BUTTONS
    # =========================

    keyboard = types.InlineKeyboardMarkup()

    approve_button = types.InlineKeyboardButton(
        "✅ Approve",
        callback_data=f"approve:{message.from_user.id}"
    )

    reject_button = types.InlineKeyboardButton(
        "❌ Reject",
        callback_data=f"reject:{message.from_user.id}"
    )

    keyboard.row(
        approve_button,
        reject_button
    )

    # =========================
    # ADMIN REQUEST
    # =========================

    username_text = (
        f"@{username}"
        if username
        else "Username নেই"
    )

    admin_text = (
        "🔔 নতুন Pending Request\n\n"
        f"👤 নাম: {name}\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"🔗 Username: {username_text}\n\n"
        "নিচের Button থেকে নির্বাচন করুন।"
    )

    bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=keyboard
    )


# =========================
# APPROVE / REJECT
# =========================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("approve:") or
        call.data.startswith("reject:")
)
def approval_handler(call):

    # শুধু Admin ব্যবহার করতে পারবে
    if call.from_user.id != ADMIN_ID:

        bot.answer_callback_query(
            call.id,
            "❌ আপনার অনুমতি নেই!",
            show_alert=True
        )

        return

    action, user_id = call.data.split(":", 1)

    users = load_users()

    # User পাওয়া না গেলে
    if user_id not in users:

        bot.answer_callback_query(
            call.id,
            "❌ User পাওয়া যায়নি!",
            show_alert=True
        )

        return

    user = users[user_id]

    # =========================
    # APPROVE
    # =========================

    if action == "approve":

        users[user_id]["status"] = "approved"
        save_users(users)

        # Admin-এর Request message update
        bot.edit_message_text(
            "✅ Request Approved\n\n"
            f"👤 নাম: {user['name']}\n"
            f"🆔 User ID: {user['id']}\n"
            + (
                f"🔗 Username: @{user['username']}\n\n"
                if user["username"]
                else "\n"
            )
            + "Status: Approved",
            call.message.chat.id,
            call.message.message_id
        )

        bot.answer_callback_query(
            call.id,
            "✅ User Approved!"
        )

        # Member-এর Pending message পরিবর্তন
        pending_message_id = user.get("pending_message_id")

        if pending_message_id:

            try:

                bot.edit_message_text(
                    "🎉 আপনার Request Approved হয়েছে!\n\n"
                    "এখন আপনি Bot ব্যবহার করতে পারবেন।",
                    int(user_id),
                    pending_message_id
                )

            except Exception:

                bot.send_message(
                    int(user_id),
                    "🎉 আপনার Request Approved হয়েছে!"
                )

        # Member-কে মূল Menu দেওয়া
        bot.send_message(
            int(user_id),
            "🏠 মূল মেনু:",
            reply_markup=main_menu()
        )

    # =========================
    # REJECT
    # =========================

    elif action == "reject":

        users[user_id]["status"] = "rejected"
        save_users(users)

        # Admin-এর message update
        bot.edit_message_text(
            "❌ Request Rejected\n\n"
            f"👤 নাম: {user['name']}\n"
            f"🆔 User ID: {user['id']}\n\n"
            "Status: Rejected",
            call.message.chat.id,
            call.message.message_id
        )

        bot.answer_callback_query(
            call.id,
            "❌ Request Rejected!"
        )

        # Member-কে জানানো
        try:

            pending_message_id = user.get("pending_message_id")

            if pending_message_id:

                bot.edit_message_text(
                    "❌ আপনার Request অনুমোদিত হয়নি।",
                    int(user_id),
                    pending_message_id
                )

            else:

                bot.send_message(
                    int(user_id),
                    "❌ আপনার Request অনুমোদিত হয়নি।"
                )

        except Exception:

            bot.send_message(
                int(user_id),
                "❌ আপনার Request অনুমোদিত হয়নি।"
            )


# =========================
# RUN BOT
# =========================

print("🤖 Bot is running...")

bot.infinity_polling(
    skip_pending=True
      )
