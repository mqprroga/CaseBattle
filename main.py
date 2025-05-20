import telebot
from telebot import types
import random
import json
import os
import time
from datetime import datetime, timedelta
from collections import OrderedDict
from collections import defaultdict
import shutil
from tempfile import NamedTemporaryFile
from datetime import datetime

bot = telebot.TeleBot(os.getenv('TOKEN'))
DATA_FILE = 'user_data.json'
REFILL_AMOUNT = 100
REFILL_COOLDOWN = 6 * 60 * 60  
INITIAL_BALANCE = 250  
BACKUP_DIR = 'backups'
os.makedirs(BACKUP_DIR, exist_ok=True)
ADMIN_USERNAME = "mqproga"  
WITHDRAW_RATE = 0.00005  
MIN_WITHDRAW = 1000  
ADMIN_CHAT_ID = '2103978046'  

collectible_items = [
    {"name": "Кинжал Лунный Свет", "price": 1200000, "emoji": "🌙"},  
    {"name": "Часы 'Золотой Век'", "price": 5000000, "emoji": "⌛"},  
    {"name": "Картина 'Крик Дракона'", "price": 8500000, "emoji": "🐉"},  
    {"name": "Кольцо Безмолвия", "price": 3200000, "emoji": "💍"},  
    {"name": "Редкий Винтажный Пончик", "price": 999999, "emoji": "🍩"},  
    {"name": "Билет на Титаник", "price": 15000000, "emoji": "🚢"}  
]

EMOJI = {
    "money": "💰",
    "case": "🎁",
    "item": "🔫",
    "back": "🔙",
    "take": "✅",
    "invest": "🔄",
    "cancel": "❌",
    "win": "🎉",
    "lose": "💀",
    "clock": "⏳",
    "top": "🏆",
    "user": "👤",
    "info": "ℹ️",  
    "common": "🟢",  
    "uncommon": "🔵",
    "rare": "🟣",
    "mythical": "🟠",
    "legendary": "🟣",
    "profile": "👤"
}

cases = OrderedDict([
    ("Базовый", {
        "price": 20,
        "emoji": "🔹",
        "items": [
            {"name": "P250 | Песочная дюна", "value": 10, "weight": 40},
            {"name": "MP9 | Песочная яма", "value": 15, "weight": 30},
            {"name": "Sawed-Off | Ржавчина", "value": 20, "weight": 20},
            {"name": "PP-Bizon | Осенний лес", "value": 25, "weight": 8},
            {"name": "MAC-10 | Пальма", "value": 30, "weight": 2}
        ]
    }),
    ("Контрактный", {
        "price": 50,
        "emoji": "📜",
        "items": [
            {"name": "Glock-18 | Водяная стихия", "value": 40, "weight": 35},
            {"name": "Desert Eagle | Кобра", "value": 50, "weight": 25},
            {"name": "AK-47 | Элитное снаряжение", "value": 55, "weight": 20},
            {"name": "M4A4 | Крушитель", "value": 60, "weight": 8},
            {"name": "AWP | Фобос", "value": 70, "weight": 2}
        ]
    }),
    ("Запретный", {
        "price": 100,
        "emoji": "🚫",
        "items": [
            {"name": "AWP | Азимов", "value": 50, "weight": 40},
            {"name": "Karambit | Ночная полоса", "value": 80, "weight": 30},
            {"name": "M4A1-S | Кибербезопасность", "value": 110, "weight": 20},
            {"name": "USP-S | Килконфирм", "value": 120, "weight": 10},
            {"name": "Desert Eagle | Прямой удар", "value": 150, "weight": 8}
        ]
    }),
    ("Легендарный", {
        "price": 200,
        "emoji": "🌟",
        "items": [
            {"name": "AWP | Дракон Лор", "value": 130, "weight": 80},
            {"name": "Karambit | Ультрафиолет", "value": 180, "weight": 20},
            {"name": "M4A4 | Королевский палач", "value": 250, "weight": 10},
            {"name": "Butterfly Knife | Лесная ночь", "value": 280, "weight": 8},
            {"name": "Desert Eagle | Блендер", "value": 320, "weight": 2}
        ]
    }),
    ("Мифический", {
        "price": 350,
        "emoji": "✨",
        "items": [
            {"name": "AWP | Медуза", "value": 270, "weight": 50},
            {"name": "Karambit | Сапфир", "value": 290, "weight": 30},
            {"name": "M4A4 | Кактус", "value": 380, "weight": 20},
            {"name": "Butterfly Knife | Фаза 2", "value": 480, "weight": 10},
            {"name": "Desert Eagle | Пламя", "value": 500, "weight": 5}
        ]
    }),
    ("Божественный", {
        "price": 500,
        "emoji": "👑",
        "items": [
            {"name": "AWP | Князь тьмы", "value": 320, "weight": 80},
            {"name": "Karambit | Рубин", "value": 456, "weight": 30},
            {"name": "M4A4 | Император", "value": 550, "weight": 20},
            {"name": "Butterfly Knife | Гамма-волна", "value": 600, "weight": 10},
            {"name": "Desert Eagle | Золотой змей", "value": 650, "weight": 8}
        ]
    }),
    ("Ангельский", {
        "price": 800,
        "emoji": "😇",
        "items": [
            {"name": "AWP | Король драконов", "value": 680, "weight": 80},
            {"name": "Karambit | Черный жемчуг", "value": 750, "weight": 20},
            {"name": "M4A4 | Последний рубеж", "value": 780, "weight": 10},
            {"name": "Butterfly Knife | Мраморный узор", "value": 800, "weight": 5},
            {"name": "Desert Eagle | Золотая катушка", "value": 850, "weight": 1}
        ]
    }),
    ("Царский", {
        "price": 1500,
        "emoji": "🫅",
        "items": [
            {"name": "AWP | Царская роскошь", "value": 950, "weight": 80},
            {"name": "AUG | Переплетение", "value": 1200, "weight": 20},
            {"name": "M4A4 | Дважды шесть", "value": 1600, "weight": 10},
            {"name": "Knife | Мрамор", "value": 1800, "weight": 5},
            {"name": "Desert Eagle | Посербренный", "value": 2000, "weight": 1}
        ]
    }),
    ("Алмазный", {
        "price": 4500,
        "emoji": "💎",
        "items": [
            {"name": "AUG | Алмазная мощь", "value": 3200, "weight": 90},
            {"name": "AWP | Драгон Лор", "value": 3700, "weight": 12},
            {"name": "Knife | Прамоутер", "value": 4500, "weight": 10},
            {"name": "M4A4 | Алмазный кран", "value": 5000, "weight": 5},
            {"name": "Desert Eagle | Тритон", "value": 5200, "weight": 1}
        ]
    })
])

def get_weighted_random_item(case_items):
    """Выбирает случайный предмет с учетом весов"""
    total_weight = sum(item["weight"] for item in case_items)
    random_num = random.uniform(0, total_weight)
    cumulative_weight = 0
    
    for item in case_items:
        cumulative_weight += item["weight"]
        if random_num <= cumulative_weight:
            return item
    
    return case_items[0]  # fallback
def reset_all_users():
    """Полностью очищает данные всех пользователей"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)
    print("Все данные пользователей были сброшены")

def repair_data_file():
    try:
        with open('user_data.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)
        print("Файл user_data.json успешно очищен")
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

def make_backup():
    """Создает резервную копию файла данных"""
    if os.path.exists(DATA_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = os.path.join(BACKUP_DIR, f"user_data_{timestamp}.json")
        shutil.copy2(DATA_FILE, backup_name)

def load_data():
    """Надежная загрузка данных с восстановлением при ошибках"""
    if not os.path.exists(DATA_FILE):
        return {}
    
    for attempt in range(3):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            backup_dir = 'backups'
            if os.path.exists(backup_dir):
                backups = sorted(
                    [f for f in os.listdir(backup_dir) if f.startswith('user_data_')],
                    reverse=True
                )
                if backups:
                    latest_backup = os.path.join(backup_dir, backups[0])
                    print(f"⚠️ Восстановление из резервной копии {latest_backup}")
                    shutil.copy2(latest_backup, DATA_FILE)
                    continue
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            if attempt == 2:
                print("⚠️ Возвращаем пустые данные из-за ошибки")
                return {}
            time.sleep(0.5)
    return {}

def save_data(data):
    """Безопасное сохранение данных с обработкой блокировок файлов"""
    max_retries = 3
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)  
    for attempt in range(max_retries):
        try:
            temp_file = None
            try:
                temp_file = NamedTemporaryFile(
                    mode='w', 
                    encoding='utf-8',
                    prefix='user_data_',
                    suffix='.tmp',
                    dir=os.path.dirname(DATA_FILE),
                    delete=False
                )
                json.dump(data, temp_file, ensure_ascii=False, indent=2)
                temp_file.close()
                if os.path.exists(DATA_FILE):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = os.path.join(backup_dir, f"user_data_{timestamp}.json")
                    shutil.copy2(DATA_FILE, backup_path)
                if os.path.exists(DATA_FILE):
                    os.replace(temp_file.name, DATA_FILE)
                else:
                    os.rename(temp_file.name, DATA_FILE)             
                return True      
            except Exception as e:
                if temp_file and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                raise          
        except PermissionError:
            if attempt == max_retries - 1:
                print(f"⚠️ Не удалось сохранить данные после {max_retries} попыток")
                return False
            time.sleep(0.5 * (attempt + 1)) 
        except Exception as e:
            print(f"Критическая ошибка сохранения: {e}")
            return False
            
    return False

def init_user(user_id, username=None):
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        data[user_id_str] = {
            "balance": INITIAL_BALANCE,
            "last_item": None,
            "last_case": None,
            "last_messages": [],
            "last_refill": None,
            "username": username or f"Игрок_{user_id}",
            "banned": False,
            "inventory": [],
            "last_messages": [], 
            "inventory": [] 
        }
    else:
        if "inventory" not in data[user_id_str]:
            data[user_id_str]["inventory"] = []
        if username:
            data[user_id_str]["username"] = username
    
    save_data(data)
    return data[user_id_str]

def update_user(user_id, key, value):
    data = load_data()
    data[str(user_id)][key] = value
    save_data(data)

def is_admin(user):
    return user.username and user.username.lower() == ADMIN_USERNAME.lower()

def add_message_to_delete(user_id, message_id):
    data = load_data()
    if "last_messages" not in data[str(user_id)]:
        data[str(user_id)]["last_messages"] = []
    data[str(user_id)]["last_messages"].append(message_id)
    save_data(data)

def clean_messages(user_id, chat_id):
    data = load_data()
    if str(user_id) in data and "last_messages" in data[str(user_id)]:
        for msg_id in data[str(user_id)]["last_messages"]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        data[str(user_id)]["last_messages"] = []
        save_data(data)

def create_main_keyboard(user_id):
    user = init_user(user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for case_name in cases:
        if user["balance"] >= cases[case_name]["price"]:
            buttons.append(types.InlineKeyboardButton(
                text=f"{cases[case_name]['emoji']} {case_name} - {cases[case_name]['price']}₽",
                callback_data=f"case_{case_name}"
            ))
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i+2])
    keyboard.row(
        types.InlineKeyboardButton(text=f"{EMOJI['money']} Пополнить (+100₽)", callback_data="refill_balance"),
        types.InlineKeyboardButton(text=f"{EMOJI['case']} Инвентарь", callback_data="show_inventory")
    )
    keyboard.row(
        types.InlineKeyboardButton(text=f"{EMOJI['top']} Топ игроков", callback_data="show_top")
    )
    
    keyboard.row(
        types.InlineKeyboardButton(text="🛒 Коллекционные предметы", callback_data="buy_collectible")
    )
    keyboard.row(
    types.InlineKeyboardButton(text=f"{EMOJI['profile']} Профили других игроков", callback_data="view_profile")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="💳 Вывести", callback_data="withdraw")
    )
    if user.get("username", "").lower() == ADMIN_USERNAME.lower():
        keyboard.row(
            types.InlineKeyboardButton(text="🛑 Забанить", callback_data="admin_ban"),
            types.InlineKeyboardButton(text="✅ Разбанить", callback_data="admin_unban")
        )
        keyboard.row(
            types.InlineKeyboardButton(text="🔁 Обнулить", callback_data="admin_reset"),
            types.InlineKeyboardButton(text="💰 Зачислить", callback_data="admin_add_money")    
        )
        keyboard.row(
            types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")     
        )
        keyboard.row(
            types.InlineKeyboardButton(text="🧺 Обнулить инвентарь", callback_data="admin_clear_inventory")   
        )
        keyboard.row(
            types.InlineKeyboardButton(text="📦 Посмотреть инвентарь", callback_data="admin_view_inventory")  # Новая кнопка
        )
    
    return keyboard

def process_withdraw_details(message, amount):
    try:
        user_id = message.from_user.id
        user = init_user(user_id)
        details = message.text.strip()
        if len(details) < 20:  # Минимальная проверка
            bot.reply_to(message, "❌ Неверный формат реквизитов")
            return
        real_amount = amount * WITHDRAW_RATE
        new_balance = user["balance"] - amount
        update_user(user_id, "balance", new_balance)
        save_withdraw_request(user_id, amount, real_amount, details)
        bot.send_message(
            message.chat.id,
            f"✅ <b>Заявка на вывод создана!</b>\n\n"
            f"💸 Сумма: {amount}₽ ({real_amount:.2f} руб.)\n"
            f"💳 Реквизиты: \n<code>{details}</code>\n\n"
            f"💰 Новый баланс: {new_balance}₽\n"
            f"⏳ Вывод обычно занимает 1-3 рабочих дня",
            parse_mode="HTML"
        )
        notify_admin(
            f"📤 Новая заявка на вывод\n"
            f"👤 Пользователь: @{user.get('username', user_id)}\n"
            f"💸 Сумма: {amount}₽ ({real_amount:.2f} руб.)\n"
            f"💳 Данные: {details}"
        )
        
    except Exception as e:
        print(f"Ошибка в process_withdraw_details: {e}")
        bot.reply_to(message, "⚠️ Ошибка при обработке реквизитов")

def save_withdraw_request(user_id, amount, real_amount, details):
    """В реальном проекте нужно сохранять в базу данных"""
    print(f"Запрос на вывод: {user_id}, {amount}₽, {real_amount} руб., {details}")

def notify_admin(text):
    """Улучшенная функция уведомления админа"""
    try:
        if not ADMIN_CHAT_ID or ADMIN_CHAT_ID == 'ВАШ_CHAT_ID':
            print("⚠️ ADMIN_CHAT_ID не настроен!")
            return False
        parts = text.split("\n")
        sensitive_data = parts[-1]
        main_message = "\n".join(parts[:-1])
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text="🔒 Показать реквизиты",
                callback_data=f"show_details_{hash(sensitive_data)}"
            )
        )
        bot.send_message(
            ADMIN_CHAT_ID,
            main_message,
            reply_markup=keyboard
        )
        global temp_details
        temp_details[hash(sensitive_data)] = sensitive_data
        
        return True
        
    except Exception as e:
        print(f"Ошибка уведомления админа: {e}")
        return False

temp_details = {}

def process_withdraw_amount(message):
    try:
        user_id = message.from_user.id
        user = init_user(user_id)  
        try:
            amount = int(message.text)
            if amount < MIN_WITHDRAW:
                bot.reply_to(message, f"❌ Сумма меньше минимальной ({MIN_WITHDRAW}₽)")
                return
            if amount > user["balance"]:
                bot.reply_to(message, "❌ Недостаточно средств на балансе")
                return
        except ValueError:
            bot.reply_to(message, "❌ Введите корректное число")
            return
        msg = bot.send_message(
            message.chat.id,
            "💳 Введите реквизиты для вывода в формате:\n"
            "<b>Банк Название\nНомер карты\nИмя держателя</b>\n\n"
            "Пример:\n"
            "Тинькофф\n5536911234567890\nИван Иванов",
            parse_mode="HTML",
            reply_markup=types.ForceReply()
        )
        bot.register_next_step_handler(
            msg, 
            lambda m: process_withdraw_details(m, amount)
        )
        
    except Exception as e:
        print(f"Ошибка в process_withdraw_amount: {e}")
        bot.reply_to(message, "⚠️ Ошибка при обработке суммы")

def create_action_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text=f"{EMOJI['take']} Забрать",
            callback_data="action_take"
        ),
        types.InlineKeyboardButton(
            text=f"{EMOJI['invest']} Вложить",
            callback_data="action_invest"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text=f"{EMOJI['back']} Назад",
            callback_data="action_back"
        )
    )
    return keyboard

def create_invest_keyboard(user_id):
    user = init_user(user_id)
    item_value = user["last_item"]["value"] if user["last_item"] else 0
    balance = user["balance"] 
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [] 
    for case_name, case_data in cases.items():
        actual_price = case_data["price"] - item_value
        if balance >= actual_price or item_value >= case_data["price"]:
            buttons.append(types.InlineKeyboardButton(
                text=f"{case_data['emoji']} {case_name}",
                callback_data=f"invest_{case_name}"
            )) 
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i+2])
    
    keyboard.add(
        types.InlineKeyboardButton(
            text=f"{EMOJI['cancel']} Отмена",
            callback_data="action_cancel"
        )
    )
    return keyboard

def make_backup():
    if os.path.exists(DATA_FILE):
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = os.path.join(backup_dir, f"user_data_{timestamp}.json")
        shutil.copy2(DATA_FILE, backup_name)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    init_user(user_id, username)
    clean_messages(user_id, message.chat.id)
    user = init_user(user_id)
    if user.get("banned", False):  # Проверка бана
        bot.send_message(message.chat.id, "⛔ Вы забанены и не можете использовать бота")
        return
    msg = bot.send_message(
        message.chat.id,
        f"{EMOJI['money']} <b>Баланс:</b> <code>{user['balance']} руб.</code>\n"
        f"{EMOJI['case']} <b>Выберите кейс:</b>",
        parse_mode="HTML",
        reply_markup=create_main_keyboard(user_id)
    )
    add_message_to_delete(user_id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'admin_view_inventory')
def admin_view_inventory_handler(call):
    """Обработчик команды 'Посмотреть инвентарь'"""
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(text="🆔 По Telegram ID", callback_data="view_inventory_by_id"),
        types.InlineKeyboardButton(text="@ По юзернейму", callback_data="view_inventory_by_username")
    )
    keyboard.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel"))  
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔢 Выберите способ для просмотра инвентаря:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == 'view_inventory_by_id')
def view_inventory_by_id_handler(call):
    """Запрашивает Telegram ID для просмотра инвентаря"""
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return 
    msg = bot.send_message(
        call.message.chat.id,
        "📝 Введите Telegram ID пользователя:",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_view_inventory_by_id)

def process_view_inventory_by_id(message):
    """Обрабатывает Telegram ID и показывает инвентарь"""
    try:
        user_id = int(message.text)
        data = load_data()      
        if str(user_id) in data:
            user = data[str(user_id)]
            inventory = user.get("inventory", [])
            if inventory:
                inventory_text = "\n".join([f"{item['name']} ({item['value']}₽)" for item in inventory])
                bot.reply_to(message, f"📦 Инвентарь пользователя с ID {user_id}:\n{inventory_text}")
            else:
                bot.reply_to(message, f"🎒 Инвентарь пользователя с ID {user_id} пуст.")
        else:
            bot.reply_to(message, f"❌ Пользователь с ID {user_id} не найден")
    except ValueError:
        bot.reply_to(message, "❌ Telegram ID должен быть числом!")

@bot.callback_query_handler(func=lambda call: call.data == 'view_profile')
def view_profile_callback(call):
    """Запрашивает юзернейм или TG ID для поиска профиля"""
    try:
        user_id = call.from_user.id
        user = init_user(user_id)      
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return
        msg = bot.send_message(
            call.message.chat.id,
            "🔍 Введите юзернейм (например, @username) или TG ID пользователя:",
            reply_markup=types.ForceReply(selective=True)
        )
        clean_messages(user_id, call.message.chat.id)
        add_message_to_delete(user_id, msg.message_id)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Ошибка в view_profile_callback: {e}")
        error_msg = bot.send_message(call.message.chat.id, "⚠️ Ошибка при запросе профиля")
        add_message_to_delete(user_id, error_msg.message_id)

@bot.message_handler(func=lambda message: message.reply_to_message and "Введите юзернейм" in message.reply_to_message.text)
def search_profile_handler(message):
    """Ищет профиль пользователя по юзернейму или ID."""
    try:
        user_id = message.from_user.id
        search_query = message.text.strip()
        data = load_data()
        if search_query.startswith("@"):
            username = search_query[1:].lower()
            target_user = next((user for user in data.values() 
                              if user.get("username", "").lower() == username), None)
        elif search_query.isdigit():
            target_user = data.get(search_query)
        else:
            bot.reply_to(message, "❌ Введите username (начинается с @) или числовой ID")
            return
        if not target_user:
            bot.reply_to(message, "❌ Пользователь не найден")
            return
        profile_text = "👤 Профиль пользователя:\n\n"
        profile_text += f"🆔 TG ID: {target_user.get('user_id', 'N/A')}\n"
        profile_text += f"👤 Юзернейм: @{target_user.get('username', 'не указан')}\n"
        profile_text += f"💰 Баланс: {target_user.get('balance', 0)} руб.\n\n"
        collectibles = [item for item in target_user.get('inventory', []) 
                       if item.get('collectible', False)]      
        if collectibles:
            profile_text += "🌟 Коллекционные скины:\n"
            for item in collectibles:
                date = item.get('purchase_date', 'дата неизвестна')
                profile_text += f"🔹 {item['name']} (куплен: {date})\n"
        else:
            profile_text += "🌟 Коллекционные скины: отсутствуют\n"
        bot.reply_to(message, profile_text)
    except Exception as e:
        print(f"Ошибка в search_profile_handler: {e}")
        bot.reply_to(message, "⚠️ Ошибка при поиске профиля")

@bot.callback_query_handler(func=lambda call: call.data == 'view_inventory_by_username')
def view_inventory_by_username_handler(call):
    """Запрашивает юзернейм для просмотра инвентаря"""
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "📝 Введите юзернейм пользователя (без @):",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_view_inventory_by_username)

def process_view_inventory_by_username(message):
    """Обрабатывает юзернейм и показывает инвентарь"""
    username_to_view = message.text.strip().lower()
    data = load_data()
    
    found = False
    for user_id, user_data in data.items():
        if user_data.get("username", "").lower() == username_to_view:
            inventory = user_data.get("inventory", [])
            if inventory:
                inventory_text = "\n".join([f"{item['name']} ({item['value']}₽)" for item in inventory])
                bot.reply_to(message, f"📦 Инвентарь пользователя @{username_to_view}:\n{inventory_text}")
            else:
                bot.reply_to(message, f"🎒 Инвентарь пользователя @{username_to_view} пуст.")
            found = True
            break
    
    if not found:
        bot.reply_to(message, f"❌ Пользователь @{username_to_view} не найден")

@bot.callback_query_handler(func=lambda call: call.data == 'admin_clear_inventory')
def admin_clear_inventory_handler(call):
    """Обработчик команды 'Обнулить инвентарь'"""
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(text="🆔 По Telegram ID", callback_data="clear_inventory_by_id"),
        types.InlineKeyboardButton(text="@ По юзернейму", callback_data="clear_inventory_by_username")
    )
    keyboard.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔢 Выберите способ для обнуления инвентаря:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == 'clear_inventory_by_id')
def clear_inventory_by_id_handler(call):
    """Запрашивает Telegram ID для обнуления инвентаря"""
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "📝 Введите Telegram ID пользователя:",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_clear_inventory_by_id)

def process_clear_inventory_by_id(message):
    """Обрабатывает Telegram ID и обнуляет инвентарь"""
    try:
        user_id = int(message.text)
        data = load_data()      
        if str(user_id) in data:
            data[str(user_id)]["inventory"] = []  # Обнуляем инвентарь
            save_data(data)
            bot.reply_to(message, f"✅ Инвентарь пользователя с ID {user_id} успешно обнулен!")
        else:
            bot.reply_to(message, f"❌ Пользователь с ID {user_id} не найден")
    except ValueError:
        bot.reply_to(message, "❌ Telegram ID должен быть числом!")

@bot.callback_query_handler(func=lambda call: call.data == 'clear_inventory_by_username')
def clear_inventory_by_username_handler(call):
    """Запрашивает юзернейм для обнуления инвентаря"""
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return  
    msg = bot.send_message(
        call.message.chat.id,
        "📝 Введите юзернейм пользователя (без @):",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_clear_inventory_by_username)

def process_clear_inventory_by_username(message):
    """Обрабатывает юзернейм и обнуляет инвентарь"""
    username_to_clear = message.text.strip().lower()
    data = load_data() 
    found = False
    for user_id, user_data in data.items():
        if user_data.get("username", "").lower() == username_to_clear:
            user_data["inventory"] = [] 
            save_data(data)
            found = True  
    if found:
        bot.reply_to(message, f"✅ Инвентарь пользователя @{username_to_clear} успешно обнулен!")
    else:
        bot.reply_to(message, f"❌ Пользователь @{username_to_clear} не найден")

@bot.callback_query_handler(func=lambda call: call.data.startswith('show_details_'))
def show_details_callback(call):
    """Показывает реквизиты админу по нажатию кнопки"""
    try:
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "❌ Доступ запрещен!")
            return          
        detail_hash = int(call.data.split('_')[2])
        details = temp_details.get(detail_hash)     
        if details:
            card_parts = details.split('\n')
            if len(card_parts) >= 2:
                card_number = card_parts[1]
                masked_card = card_number[:6] + '*'*(len(card_number)-10) + card_number[-4:]
                card_parts[1] = masked_card
                masked_details = '\n'.join(card_parts)
            else:
                masked_details = details       
            bot.send_message(
                call.message.chat.id,
                f"🔐 <b>Реквизиты:</b>\n<code>{masked_details}</code>",
                parse_mode="HTML"
            )
            bot.answer_callback_query(call.id)
            temp_details.pop(detail_hash, None)
        else:
            bot.answer_callback_query(call.id, "⚠️ Данные не найдены или устарели")          
    except Exception as e:
        print(f"Ошибка в show_details_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Ошибка при получении данных")

def process_withdraw_details(message, amount):
    try:
        user_id = message.from_user.id
        user = init_user(user_id)      
        details = message.text.strip()
        if len(details) < 20 or '\n' not in details:
            bot.reply_to(message, "❌ Неверный формат. Укажите банк, номер карты и имя, каждый с новой строки")
            return        
        real_amount = amount * WITHDRAW_RATE
        new_balance = user["balance"] - amount
        update_user(user_id, "balance", new_balance)
        admin_msg = (
            f"📤 Новая заявка на вывод\n"
            f"👤 Пользователь: @{user.get('username', user_id)}\n"
            f"🆔 ID: {user_id}\n"
            f"💸 Сумма: {amount}₽ ({real_amount:.2f} руб.)\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"{details}"  # Реквизиты будут обработаны в notify_admin
        )
        if not notify_admin(admin_msg):
            bot.reply_to(message, "⚠️ Администратор временно недоступен. Попробуйте позже")
            return
        bot.send_message(
            message.chat.id,
            f"✅ <b>Заявка #{hash(details)%10000} принята!</b>\n\n"
            f"💸 Сумма: {amount}₽ ({real_amount:.2f} руб.)\n"
            f"💰 Новый баланс: {new_balance}₽\n\n"
            f"⏳ Обработка заявки занимает до 24 часов\n"
            f"📩 По вопросам: @{ADMIN_USERNAME}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Ошибка в process_withdraw_details: {e}")
        bot.reply_to(message, "⚠️ Ошибка при обработке заявки")

@bot.callback_query_handler(func=lambda call: call.data.startswith('case_'))
def case_callback(call):
    try:
        user_id = call.from_user.id
        case_name = call.data.split('_')[1]
        case = cases[case_name]
        user = init_user(user_id)       
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return
        if user["balance"] < case["price"]:
            bot.answer_callback_query(call.id, "Недостаточно средств!")
            return
        new_balance = user["balance"] - case["price"]
        update_user(user_id, "balance", new_balance)
        item = get_weighted_random_item(case["items"])
        update_user(user_id, "last_item", item)
        update_user(user_id, "last_case", case_name)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton(text=f"{EMOJI['take']} Забрать (+{item['value']}₽)", 
                                     callback_data="action_take"),
            types.InlineKeyboardButton(text=f"{EMOJI['invest']} Вложить", 
                                     callback_data="action_invest")
        )
        bot.send_message(
            call.message.chat.id,
            f"{EMOJI['win']} <b>Вы открыли {case_name} кейс!</b>\n\n"
            f"{EMOJI['item']} <b>Предмет:</b> <code>{item['name']}</code>\n"
            f"{EMOJI['money']} <b>Цена:</b> <code>{item['value']}₽</code>\n"
            f"{EMOJI['info']} <b>Редкость:</b> {get_rarity_emoji(item['weight'])}\n\n"
            f"{EMOJI['money']} <b>Баланс:</b> <code>{new_balance}₽</code>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в case_callback: {e}")
        bot.send_message(call.message.chat.id, "⚠️ Ошибка при открытии кейса")

def get_rarity_emoji(weight):
    """Возвращает эмодзи и название редкости"""
    if weight >= 30: return f"{EMOJI['common']} Обычный"
    elif weight >= 15: return f"{EMOJI['uncommon']} Необычный"
    elif weight >= 5: return f"{EMOJI['rare']} Редкий"
    elif weight >= 2: return f"{EMOJI['mythical']} Мифический"
    else: return f"{EMOJI['legendary']} Легендарный"

@bot.callback_query_handler(func=lambda call: call.data == 'buy_collectible')
def buy_collectible_handler(call):
    """Показывает меню для покупки коллекционных предметов"""
    user_id = call.from_user.id
    user = init_user(user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for item in collectible_items:
        if user["balance"] >= item["price"]:
            keyboard.add(types.InlineKeyboardButton(
                text=f"{item['emoji']} {item['name']} - {item['price']:,} руб.",  # Заменяем ₽ на руб.
                callback_data=f"buy_item_{item['name']}"
            ))
        else:
            keyboard.add(types.InlineKeyboardButton(
                text=f"❌ {item['emoji']} {item['name']} - {item['price']:,} руб. (Недостаточно средств)",  # Заменяем ₽ на руб.
                callback_data="not_enough_balance"
            ))
    keyboard.add(types.InlineKeyboardButton(text=f"{EMOJI['back']} Назад", callback_data="action_back"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🛒 Выберите коллекционный предмет для покупки:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == 'not_enough_balance')
def not_enough_balance_handler(call):
    """Обрабатывает нажатие на недоступный предмет"""
    bot.answer_callback_query(call.id, "❌ Недостаточно средств для покупки!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_item_'))
def buy_item_handler(call):
    """Обрабатывает покупку коллекционного предмета"""
    user_id = call.from_user.id
    user = init_user(user_id)
    
    item_name = call.data.split('_', 3)[2]
    item = next((item for item in collectible_items if item["name"] == item_name), None)
    
    if not item:
        bot.answer_callback_query(call.id, "❌ Ошибка: предмет не найден!", show_alert=True)
        return
    
    # Проверяем баланс
    if user["balance"] < item["price"]:
        bot.answer_callback_query(call.id, "❌ Недостаточно средств!", show_alert=True)
        return
    
    # Покупка предмета
    user["balance"] -= item["price"]
    user["inventory"].append({
        "name": item["name"],
        "value": item["price"],
        "collectible": True,
        "purchase_date": datetime.now().strftime("%d.%m.%Y %H:%M")  # Сохраняем дату покупки
    })
    update_user(user_id, "balance", user["balance"])
    update_user(user_id, "inventory", user["inventory"])
    
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"🎉 Вы успешно купили {item['emoji']} <b>{item['name']}</b> за {item['price']:,} руб.!",
        parse_mode="HTML",
        reply_markup=create_main_keyboard(user_id)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'show_inventory')
def inventory_callback(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        user = init_user(user_id)
        
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return
        
        clean_messages(user_id, chat_id)
        
        if not user.get("inventory", []):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{EMOJI['back']} Назад",
                    callback_data="action_back"
                )
            )
            msg = bot.send_message(
                chat_id,
                "🎒 Ваш инвентарь пуст",
                reply_markup=keyboard
            )
            add_message_to_delete(user_id, msg.message_id)
            return
        
        keyboard = types.InlineKeyboardMarkup()
        
        # Кнопка быстрой продажи
        if user["inventory"]:
            total_value = sum(item["value"] for item in user["inventory"])
            sell_all_price = int(total_value * 0.55)
            keyboard.add(
                types.InlineKeyboardButton(
text=f"⚡ Продать все ({len(user['inventory'])}) → {sell_all_price}₽",
                    callback_data="sell_all_items"
                )
            )
        
        # Кнопки для отдельных предметов
        for index, item in enumerate(user["inventory"]):
            sell_price = int(item["value"] * 0.55)
            keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{item['name']} ({item['value']}₽ → {sell_price}₽)",
                    callback_data=f"sell_item_{index}"
                )
            )
        
        # Кнопка назад
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{EMOJI['back']} Назад",
                callback_data="action_back"
            )
        )
        
        msg = bot.send_message(
            chat_id, 
            f"🎒 *Ваш инвентарь:*\nПродажа за 55% от стоимости\n📦 Предметов: {len(user['inventory'])}",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        add_message_to_delete(user_id, msg.message_id)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в inventory_callback: {e}")
        error_msg = bot.send_message(chat_id, "⚠️ Ошибка загрузки инвентаря")
        add_message_to_delete(user_id, error_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'sell_all_items')
def sell_all_items_callback(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        user = init_user(user_id)
        
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return
        
        if not user.get("inventory", []):
            bot.answer_callback_query(call.id, "❌ Инвентарь пуст!")
            return
        
        # Фильтруем только не коллекционные предметы
        items_to_sell = [item for item in user["inventory"] if not item.get("collectible", False)]
        collectible_items = [item for item in user["inventory"] if item.get("collectible", False)]
        
        if not items_to_sell:
            bot.answer_callback_query(call.id, "❌ Нет предметов для продажи (только коллекционные)!", show_alert=True)
            return
        
        # Расчет суммы продажи
        total = sum(item["value"] for item in items_to_sell)
        amount = int(total * 0.55)
        count = len(items_to_sell)
        
        # Обновление данных
        new_balance = user["balance"] + amount
        update_user(user_id, "balance", new_balance)
        # Сохраняем только коллекционные предметы
        update_user(user_id, "inventory", collectible_items)
        
        # Сообщение о продаже
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text=f"{EMOJI['back']} В меню", callback_data="action_back"))
        
        msg = bot.send_message(
            chat_id,
            f"⚡ *Продано {count} предметов!*\n\n"
            f"• Общая стоимость: {total}₽\n"
            f"• Получено: {amount}₽ (55%)\n"
            f"• Новый баланс: {new_balance}₽\n\n"
            f"• Коллекционные предметы сохранены",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        clean_messages(user_id, chat_id)
        add_message_to_delete(user_id, msg.message_id)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в sell_all_items_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Ошибка при продаже")
        error_msg = bot.send_message(chat_id, "⚠️ Не удалось продать предметы")
        add_message_to_delete(user_id, error_msg.message_id)



# Добавьте эту команду для админа, если нужно
@bot.message_handler(commands=['clear_backups'])
def clear_backups(message):
    if not is_admin(message.from_user):
        return
    for filename in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, filename)
        try:
            os.remove(file_path)
        except:
            pass
    bot.reply_to(message, "✅ Бэкапы очищены!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('sell_item_'))
def sell_item_callback(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        user = init_user(user_id)
        
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return
        
        item_index = int(call.data.split('_')[2])
        
        # Проверяем существует ли предмет
        if item_index >= len(user["inventory"]):
            bot.answer_callback_query(call.id, "❌ Предмет не найден!")
            return
        
        item = user["inventory"][item_index]
        
        # Проверяем, является ли предмет коллекционным
        if item.get("collectible", False):
            bot.answer_callback_query(call.id, "❌ Коллекционные предметы нельзя продать!", show_alert=True)
            return
        
        # Продажа предмета
        sell_price = int(item["value"] * 0.55)  # 35% от стоимости
        user["balance"] += sell_price
        user["inventory"].pop(item_index)
        update_user(user_id, "balance", user["balance"])
        update_user(user_id, "inventory", user["inventory"])
        
        # Создаем клавиатуру для возврата
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{EMOJI['back']} В инвентарь",
                callback_data="show_inventory"
            )
        )
        
        # Отправляем подтверждение продажи
        msg = bot.send_message(
            chat_id,
            f"✅ *Предмет продан!*\n\n"
            f"🔹 *Название:* {item['name']}\n"
            f"💰 *Оригинальная цена:* {item['value']}₽\n"
            f"💵 *Вы получили:* {sell_price}₽ (35%)\n\n"
            f"📊 *Новый баланс:* {user['balance']}₽",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        clean_messages(user_id, chat_id)
        add_message_to_delete(user_id, msg.message_id)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в sell_item_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Ошибка при продаже предмета")
        error_msg = bot.send_message(chat_id, "⚠️ Ошибка при продаже предмета")
        add_message_to_delete(user_id, error_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'action_take')
def take_callback(call):
    try:
        user_id = call.from_user.id
        user = init_user(user_id)
        
        if not user.get("last_item"):
            bot.answer_callback_query(call.id, "Нет предмета для забора!")
            return
        
        # Добавляем стоимость предмета к балансу
        item_value = user["last_item"]["value"]
        new_balance = user["balance"] + item_value
        update_user(user_id, "balance", new_balance)
        update_user(user_id, "last_item", None)
        
        # Добавляем в инвентарь
        user["inventory"].append(user["last_item"])
        update_user(user_id, "inventory", user["inventory"])
        
        bot.send_message(
            call.message.chat.id,
            f"✅ {EMOJI['money']} <b>Предмет добавлен в инвентарь!</b>\n"
            f"💰 <b>Получено:</b> +{item_value}₽\n"
            f"💵 <b>Баланс:</b> {new_balance}₽",
            parse_mode="HTML",
            reply_markup=create_main_keyboard(user_id)
        )
        bot.answer_callback_query(call.id)
        
        # Проверка на конец игры
        if new_balance <= 0:
            game_over(call.message.chat.id, user_id)
            
    except Exception as e:
        print(f"Ошибка в take_callback: {e}")
        bot.send_message(call.message.chat.id, "⚠️ Ошибка при сохранении предмета")

@bot.callback_query_handler(func=lambda call: call.data == 'action_invest')
def invest_callback(call):
    try:
        user_id = call.from_user.id
        user = init_user(user_id)
        
        if not user["last_item"]:
            bot.answer_callback_query(call.id, "Нет предмета для вложения!")
            return
        
        clean_messages(user_id, call.message.chat.id)
        
        # Создаем клавиатуру с доступными кейсами
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        for case_name, case_data in cases.items():
            item_value = user["last_item"]["value"]
            actual_price = max(0, case_data["price"] - item_value)
            
            # Проверяем доступность кейса
            if user["balance"] >= actual_price or item_value >= case_data["price"]:
                # Особые условия для кейса "Мажор"
                if case_name == "Мажор" and (user["balance"] + item_value) < 150:
                    continue
                    
                buttons.append(types.InlineKeyboardButton(
                    text=f"{case_data['emoji']} {case_name} ({actual_price}₽)",
                    callback_data=f"invest_{case_name}"
                ))
        
        # Разбиваем кнопки на ряды
        for i in range(0, len(buttons), 2):
            keyboard.add(*buttons[i:i+2])
        
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{EMOJI['cancel']} Отмена",
                callback_data="action_cancel"
            )
        )
        
        msg = bot.send_message(
            call.message.chat.id,
            f"{EMOJI['invest']} <b>Выберите кейс для вложения:</b>\n\n"
            f"{EMOJI['item']} <b>Предмет:</b> <code>{user['last_item']['name']}</code>\n"
            f"{EMOJI['money']} <b>Цена:</b> <code>{user['last_item']['value']}₽</code>\n\n"
            f"{EMOJI['money']} <b>Баланс:</b> <code>{user['balance']}₽</code>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        add_message_to_delete(user_id, msg.message_id)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в invest_callback: {e}")
        bot.send_message(call.message.chat.id, "⚠️ Ошибка при выборе кейса")

@bot.callback_query_handler(func=lambda call: call.data == 'withdraw')
def withdraw_callback(call):
    try:
        user_id = call.from_user.id
        user = init_user(user_id)
        
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return
        
        # Проверяем минимальную суммуs
        if user["balance"] < MIN_WITHDRAW:
            bot.answer_callback_query(
                call.id, 
                f"❌ Минимальная сумма вывода: {MIN_WITHDRAW}₽", 
                show_alert=True
            )
            return
            
        # Запрашиваем сумму вывода
        msg = bot.send_message(
            call.message.chat.id,
            f"💰 <b>Доступно для вывода:</b> {user['balance']}₽ (~{user['balance']*WITHDRAW_RATE:.2f} руб.)\n"
            f"📌 Минимальная сумма: {MIN_WITHDRAW}₽\n\n"
            "Введите сумму для вывода:",
            parse_mode="HTML",
            reply_markup=types.ForceReply()
        )
        bot.register_next_step_handler(msg, process_withdraw_amount)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в withdraw_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Ошибка при выводе средств")


@bot.callback_query_handler(func=lambda call: call.data == 'admin_unban')
def admin_unban_handler(call):
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "Введите username пользователя для разбана (без @):",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_unban_user)

def process_unban_user(message):
    username_to_unban = message.text.strip().lower()
    data = load_data()
    found = False
    
    for user_id, user_data in data.items():
        if user_data.get("username", "").lower() == username_to_unban:
            user_data["banned"] = False
            found = True
    
    if found:
        save_data(data)
        bot.reply_to(message, f"✅ Пользователь @{username_to_unban} разбанен!")
    else:
        bot.reply_to(message, f"❌ Пользователь @{username_to_unban} не найден")

# Вспомогательная функция для проверки админа
def is_admin(user):
    return user.username and user.username.lower() == ADMIN_USERNAME.lower()

@bot.callback_query_handler(func=lambda call: call.data.startswith('invest_'))
def invest_case_callback(call):
    try:
        user_id = call.from_user.id
        case_name = call.data.split('_')[1]
        case = cases[case_name]
        user = init_user(user_id)
        
        if not user["last_item"]:
            bot.answer_callback_query(call.id, "Ошибка: предмет не найден!")
            return
        
        item_value = user["last_item"]["value"]
        actual_price = max(0, case["price"] - item_value)
        
        # Проверка баланса
        if user["balance"] < actual_price and item_value < case["price"]:
            bot.answer_callback_query(call.id, "Недостаточно средств!")
            return
        
        # Особые условия для кейса "Мажор"
        if case_name == "Мажор" and (user["balance"] + item_value) < 150:
            bot.answer_callback_query(call.id, "Для этого кейса нужно минимум 150₽ с учетом предмета!")
            return
        
        # Обновляем баланс
        change = item_value - case["price"]
        new_balance = user["balance"] + change if change > 0 else user["balance"] - actual_price
        update_user(user_id, "balance", new_balance)
        update_user(user_id, "last_item", None)
        
        # Открываем новый кейс
        new_item = random.choice(case["items"])
        update_user(user_id, "last_item", new_item)
        update_user(user_id, "last_case", case_name)
        
        # Формируем сообщение о результате
        message = [
            f"{EMOJI['win']} <b>Вы открыли {case_name} кейс!</b>",
            f"{EMOJI['item']} <b>Новый предмет:</b> <code>{new_item['name']}</code>",
            f"{EMOJI['money']} <b>Цена:</b> <code>{new_item['value']}₽</code>"
        ]
        
        if change > 0:
            message.append(f"{EMOJI['money']} <b>Возвращено:</b> +{change}₽")
        
        message.append(f"{EMOJI['money']} <b>Баланс:</b> <code>{new_balance}₽</code>")
        
        # Клавиатура действий
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton(text=f"{EMOJI['take']} Забрать (+{new_item['value']}₽)", callback_data="action_take"),
            types.InlineKeyboardButton(text=f"{EMOJI['invest']} Вложить", callback_data="action_invest")
        )
        
        bot.send_message(
            call.message.chat.id,
            "\n\n".join(message),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
        if new_balance <= 0:
            time.sleep(2)
            game_over(call.message.chat.id, user_id)
            
    except Exception as e:
        print(f"Ошибка в invest_case_callback: {e}")
        bot.send_message(call.message.chat.id, "⚠️ Ошибка при вложении предмета")

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_by_'))
def choose_add_method(call):
    method = call.data.split('_')[-1]
    if method == "id":
        prompt = "📝 Введите Telegram ID и сумму через пробел:\nПример: <code>123456789 500</code>"
    elif method == "username":
        prompt = "📝 Введите юзернейм (без @) и сумму через пробел:\nПример: <code>username 500</code>"
    else:
        bot.answer_callback_query(call.id, "❌ Неверный метод")
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        prompt,
        parse_mode="HTML",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, lambda m: process_payment(m, method))
def process_payment(message, method):
    try:
        if not is_admin(message.from_user):
            bot.reply_to(message, "❌ Доступ запрещен!")
            return
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) != 2:
            bot.reply_to(message, "❌ Неверный формат. Нужно: [юзернейм/ID] [сумма]")
            return
        identifier, amount_str = parts
        try:
            amount = int(amount_str)
            if amount <= 0:
                bot.reply_to(message, "❌ Сумма должна быть положительной!")
                return
        except ValueError:
            bot.reply_to(message, "❌ Сумма должна быть числом!")
            return
        data = load_data()    
        if method == "id":
            try:
                user_id = int(identifier)
                user_data = data.get(str(user_id))
                if not user_data:
                    bot.reply_to(message, f"❌ Пользователь с ID {user_id} не найден!")
                    return
            except ValueError:
                bot.reply_to(message, "❌ Telegram ID должен быть числом!")
                return
        else:
            clean_username = identifier.lstrip('@').lower()
            found_users = [(uid, u) for uid, u in data.items() 
                         if u.get('username', '').lower() == clean_username]  
            if not found_users:
                bot.reply_to(message, f"❌ Пользователь @{clean_username} не найден!")
                return
            if len(found_users) > 1:
                bot.reply_to(message, f"⚠️ Найдено {len(found_users)} пользователей. Используйте ID")
                return
            user_id, user_data = found_users[0]
        old_balance = user_data.get("balance", 0)
        new_balance = old_balance + amount
        user_data["balance"] = new_balance
        save_data(data)
        recipient = f"@{user_data.get('username', '')}" if method == "username" else f"ID {user_id}"
        response = (
            f"✅ Успешное зачисление!\n\n"
            f"👤 Получатель: {recipient}\n"
            f"💰 Было: {old_balance}₽\n"
            f"💵 Зачислено: +{amount}₽\n"
            f"💳 Новый баланс: {new_balance}₽"
        )  
        bot.reply_to(message, response)
        try:
            bot.send_message(
                user_id,
                f"🎉 Администратор зачислил вам {amount}₽!\n"
                f"💰 Ваш баланс: {new_balance}₽"
            )
        except Exception as e:
            print(f"Не удалось уведомить пользователя {user_id}: {e}")
    except Exception as e:
        print(f"Ошибка в process_payment: {e}")
        bot.reply_to(message, "⚠️ Ошибка при обработке запроса")
def process_admin_add_money(message):
    try:
        global current_payment_method
        method = current_payment_method
        if not is_admin(message.from_user):
            bot.reply_to(message, "❌ Доступ запрещен!")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Неверный формат. Нужно: [ID/юзернейм] [сумма]")
            return
        identifier, amount_str = parts
        try:
            amount = int(amount_str)
            if amount <= 0:
                bot.reply_to(message, "❌ Сумма должна быть положительной!")
                return
        except ValueError:
            bot.reply_to(message, "❌ Сумма должна быть числом!")
            return
        data = load_data()
        user = None
        if method == "id":
            try:
                user_id = int(identifier)
                user = data.get(str(user_id))
                if not user:
                    bot.reply_to(message, f"❌ Пользователь с ID {user_id} не найден!")
                    return
            except ValueError:
                bot.reply_to(message, "❌ Telegram ID должен быть числом!")
                return
        else:
            clean_username = identifier.lstrip('@').lower()
            found_users = [
                (uid, u) for uid, u in data.items() 
                if u.get('username', '').lower() == clean_username
            ]
            
            if not found_users:
                bot.reply_to(message, f"❌ Пользователь @{clean_username} не найден!")
                return
            if len(found_users) > 1:
                bot.reply_to(message, f"⚠️ Найдено {len(found_users)} пользователей. Используйте ID для точности")
                return
            user_id, user = found_users[0]
        old_balance = user.get("balance", 0)
        new_balance = old_balance + amount
        user["balance"] = new_balance
        save_data(data)

        reply_text = [
            f"✅ Успешное зачисление!",
            f"👤 Получатель: {'@' + user.get('username', '') if method == 'username' else 'ID: ' + str(user_id)}",
            f"💰 Было: {old_balance}₽",
            f"💵 Зачислено: +{amount}₽",
            f"💳 Новый баланс: {new_balance}₽"
        ]
        
        bot.reply_to(message, "\n".join(reply_text))

        try:
            bot.send_message(
                user_id,
                f"🎉 Администратор зачислил вам {amount}₽!\n"
                f"💰 Ваш баланс: {new_balance}₽"
            )
        except Exception as e:
            print(f"Не удалось уведомить пользователя: {e}")

    except Exception as e:
        print(f"Ошибка в process_admin_add_money: {e}")
        bot.reply_to(message, "⚠️ Произошла ошибка при зачислении")

@bot.callback_query_handler(func=lambda call: call.data == 'refill_balance')
def refill_balance_callback(call):
    try:
        user_id = call.from_user.id
        user = init_user(user_id)
        
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return

        current_time = datetime.now()
        last_refill = user.get("last_refill")
        
        if last_refill:
            last_refill = datetime.strptime(last_refill, "%Y-%m-%d %H:%M:%S")
            time_left = (last_refill + timedelta(hours=6)) - current_time
            
            if time_left.total_seconds() > 0:
                hours = time_left.seconds // 3600
                minutes = (time_left.seconds % 3600) // 60
                bot.answer_callback_query(
                    call.id, 
                    f"⏳ Следующее пополнение через {hours}ч {minutes}м", 
                    show_alert=True
                )
                return

        current_balance = user["balance"]
        new_balance = current_balance + REFILL_AMOUNT
        update_user(user_id, "balance", new_balance)
        update_user(user_id, "last_refill", current_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        bot.send_message(
            call.message.chat.id,
            f"{EMOJI['money']} <b>Баланс пополнен на {REFILL_AMOUNT}₽!</b>\n"
            f"💰 <b>Было:</b> {current_balance}₽\n"
            f"💵 <b>Стало:</b> {new_balance}₽\n\n"
            f"⏳ Следующее пополнение будет доступно через 6 часов",
            parse_mode="HTML",
            reply_markup=create_main_keyboard(user_id)
        )
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в refill_balance_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Ошибка при пополнении баланса")

@bot.callback_query_handler(func=lambda call: call.data == 'admin_ban')
def admin_ban_handler(call):
    
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "Введите username пользователя для бана (без @):",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_ban_user)

def process_ban_user(message):
    username_to_ban = message.text.strip()
    data = load_data()
    
    for user_id, user_data in data.items():
        if user_data.get("username", "").lower() == username_to_ban.lower():
            user_data["banned"] = True
            save_data(data)
            bot.reply_to(message, f"Пользователь @{username_to_ban} забанен!")
            return
    
    bot.reply_to(message, f"Пользователь @{username_to_ban} не найден")

@bot.callback_query_handler(func=lambda call: call.data == 'admin_reset')
def admin_reset_handler(call):

    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "Введите username пользователя для обнуления (без @):",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_reset_user)

def process_reset_user(message):
    username_to_reset = message.text.strip()
    data = load_data()
    
    for user_id, user_data in data.items():
        if user_data.get("username", "").lower() == username_to_reset.lower():
            user_data.update({
                "balance": INITIAL_BALANCE,
                "last_item": None,
                "last_case": None
            })
            save_data(data)
            bot.reply_to(message, f"Прогресс пользователя @{username_to_reset} обнулен!")
            return
    
    bot.reply_to(message, f"Пользователь @{username_to_reset} не найден")

@bot.callback_query_handler(func=lambda call: call.data == 'admin_stats')
def admin_stats_handler(call):
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    try:
        data = load_data()
        total_users = len(data)
        active_users = sum(1 for user in data.values() if user.get('balance', 0) > 0)
        total_balance = sum(user.get('balance', 0) for user in data.values())
        banned_users = sum(1 for user in data.values() if user.get('banned', False))
        case_stats = {case: 0 for case in cases}
        for user in data.values():
            if 'last_case' in user and user['last_case'] in case_stats:
                case_stats[user['last_case']] += 1
        stats_message = (
            f"📊 <b>Статистика бота:</b>\n\n"
            f"👥 <b>Всего пользователей:</b> {total_users}\n"
            f"👤 <b>Активных:</b> {active_users}\n"
            f"⛔ <b>Забанено:</b> {banned_users}\n"
            f"💰 <b>Общий баланс:</b> {total_balance}₽\n\n"
            f"📦 <b>Открытия кейсов:</b>\n"
        )
        for case, count in case_stats.items():
            stats_message += f"  {cases[case]['emoji']} {case}: {count}\n"
        top_users = sorted(
            [(u['username'], u.get('balance', 0)) 
             for u in data.values() 
             if 'username' in u],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        stats_message += "\n🏆 <b>Топ-5 игроков:</b>\n"
        for i, (username, balance) in enumerate(top_users, 1):
            stats_message += f"{i}. {username}: {balance}₽\n"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text="🔄 Обновить",
                callback_data="admin_stats"
            ),
            types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="action_back"
            )
        )     
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=stats_message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except:
            bot.send_message(
                call.message.chat.id,
                stats_message,
                parse_mode="HTML",
                reply_markup=keyboard
            )      
        bot.answer_callback_query(call.id) 
    except Exception as e:
        print(f"Ошибка в admin_stats_handler: {e}")
        bot.answer_callback_query(call.id, "⚠️ Ошибка загрузки статистики")

@bot.callback_query_handler(func=lambda call: call.data == 'show_top')
def show_top_callback(call):
    try:
        user_id = call.from_user.id
        user = init_user(user_id)    
        if user.get("banned", False):
            bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
            return     
        data = load_data()
        valid_users = []
        for user_data in data.values():
            if not all(key in user_data for key in ['username', 'balance']):
                continue
            username = user_data['username'] or f"Игрок_{id}"
            valid_users.append({
                'username': username,
                'balance': user_data['balance']
            })
        top_users = sorted(valid_users, key=lambda x: x['balance'], reverse=True)[:10]
        top_text = f"{EMOJI['top']} <b>Топ игроков:</b>\n\n"
        for i, player in enumerate(top_users, 1):
            top_text += f"{i}. {player['username']}: {player['balance']}₽\n"
        current_username = user.get('username', f"Игрок_{user_id}")
        if not any(p['username'] == current_username for p in top_users):
            user_balance = user.get('balance', 0)
            user_position = next((i+1 for i, p in enumerate(valid_users) 
                               if p['username'] == current_username), '>10')
            top_text += f"\n...\nВаше место: {user_position}. {current_username}: {user_balance}₽"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f"{EMOJI['back']} Назад",
            callback_data="action_back"
        ))
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=top_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except:
            bot.send_message(
                call.message.chat.id,
                top_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка в show_top_callback: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки топа")
        print(f"Данные пользователей: {data}")  # Посмотреть структуру данных

@bot.callback_query_handler(func=lambda call: call.data == 'admin_add_money')
def admin_add_money_handler(call):
    if not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "❌ Недостаточно прав!", show_alert=True)
        return
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(text="🆔 По ID", callback_data="add_by_id"),
        types.InlineKeyboardButton(text="@ По юзернейму", callback_data="add_by_username")
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔢 Выберите способ зачисления:",
        reply_markup=keyboard
    )

def process_admin_add_money(message):
    try:
        if not is_admin(message.from_user):
            bot.reply_to(message, "❌ Доступ запрещен!")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Неверный формат. Используйте: ID Сумма")
            return

        user_id, amount = parts
        try:
            user_id = int(user_id)
            amount = int(amount)  
            if amount <= 0:
                bot.reply_to(message, "❌ Сумма должна быть положительной!")
                return
        except ValueError:
            bot.reply_to(message, "❌ ID и сумма должны быть числами!")
            return
        data = load_data()
        user_id_str = str(user_id)
        if user_id_str not in data:
            bot.reply_to(message, f"❌ Пользователь с ID {user_id} не найден!")
            return
        user_data = data[user_id_str]
        old_balance = user_data.get("balance", 0)
        new_balance = old_balance + amount
        user_data["balance"] = new_balance
        save_data(data)
        bot.reply_to(
            message,
            f"✅ Успешное зачисление!\n\n"
            f"👤 ID: {user_id}\n"
            f"💰 Было: {old_balance}₽\n"
            f"💵 Зачислено: +{amount}₽\n"
            f"💳 Стало: {new_balance}₽"
        )
        try:
            bot.send_message(
                user_id,
                f"🎉 Администратор зачислил вам {amount}₽!\n"
                f"💰 Ваш баланс: {new_balance}₽"
            )
        except:
            print(f"Не удалось уведомить пользователя {user_id}")

    except Exception as e:
        print(f"Ошибка в process_admin_add_money: {e}")
        bot.reply_to(message, "⚠️ Произошла ошибка при зачислении")

@bot.callback_query_handler(func=lambda call: call.data in ['action_back', 'action_cancel'])
def back_callback(call):
    user = init_user(call.from_user.id)
    if user.get("banned", False):
        bot.answer_callback_query(call.id, "⛔ Вы забанены!", show_alert=True)
        return
    user_id = call.from_user.id
    user = init_user(user_id)
    
    clean_messages(user_id, call.message.chat.id)
    
    if call.data == 'action_cancel' and user["last_item"]:
        new_balance = user["balance"] + user["last_item"]["value"]
        update_user(user_id, "balance", new_balance)
        update_user(user_id, "last_item", None)
    
    msg = bot.send_message(
        call.message.chat.id,
        f"{EMOJI['money']} <b>Баланс:</b> <code>{user['balance']} руб.</code>\n"
        f"{EMOJI['case']} <b>Выберите кейс:</b>",
        parse_mode="HTML",
        reply_markup=create_main_keyboard(user_id)
    )
    
    add_message_to_delete(user_id, msg.message_id)
    bot.answer_callback_query(call.id)

def game_over(chat_id, user_id):
    clean_messages(user_id, chat_id)
    update_user(user_id, "balance", INITIAL_BALANCE)
    update_user(user_id, "last_item", None)
    update_user(user_id, "last_case", None)
    update_user(user_id, "last_refill", None)
    
    msg = bot.send_message(
        chat_id,
        f"{EMOJI['lose']} <b>Игра окончена! Ваш баланс опустился до 0.</b>\n\n"
        f"{EMOJI['money']} <b>Стартовый баланс:</b> <code>{INITIAL_BALANCE} руб.</code>\n\n"
        "Нажмите /start чтобы начать заново",
        parse_mode="HTML"
    )
    
    add_message_to_delete(user_id, msg.message_id)

def repair_data():
    """Восстанавливает поврежденные данные"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                json.load(f)
        except:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)

repair_data()

if __name__ == '__main__':
    print("Бот запущен...")
    try:
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)    
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        save_data(load_data())
