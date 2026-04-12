#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║     DIAS TARGETPRO — TELEGRAM NOTIFICATION BOT               ║
║     Уведомляет Диаса о каждой заявке и оплате с сайта        ║
╚══════════════════════════════════════════════════════════════╝

УСТАНОВКА И ЗАПУСК:
───────────────────
1. Установи Python 3.8+ если нет: https://python.org

2. Установи библиотеку:
   pip install pyTelegramBotAPI requests flask

3. Создай бота:
   → Открой Telegram, найди @BotFather
   → Напиши /newbot
   → Придумай имя: DiasTargetPro Bot
   → Получи токен вида: 1234567890:ABCDEFghijklmnop...
   → Вставь его в BOT_TOKEN ниже

4. Узнай свой Chat ID:
   → Напиши своему боту любое сообщение
   → Открой: https://api.telegram.org/bot<ТОЙ_ТОКЕН>/getUpdates
   → Найди "chat":{"id": XXXXXXXX} — это твой CHAT_ID

5. Вставь токен и chat_id в сайт (dias_landing.html):
   var TG_BOT_TOKEN = 'твой_токен';
   var TG_CHAT_ID   = 'твой_chat_id';

6. Запусти бота:
   python dias_bot.py

ПРИМЕЧАНИЕ:
   Сайт отправляет уведомления напрямую в Telegram API.
   Этот файл — дополнительный бот с командами /stats и /export.
"""

import telebot
import json
import os
from datetime import datetime
from collections import defaultdict

# ╔═══════════════════════════════════╗
# ║  НАСТРОЙКИ — ЗАПОЛНИ ЭТО!        ║
# ╚═══════════════════════════════════╝
BOT_TOKEN = '8553303124:AAF5sWT6X7GutiDDJ7kxlgVrqqgNND1x83c'   # Токен от @BotFather
ADMIN_ID  = '5138222484'     # Твой Telegram chat_id

DB_FILE = 'leads_db.json'

bot = telebot.TeleBot(BOT_TOKEN)

# ══ БАЗА ДАННЫХ (простой JSON файл) ══
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'leads': [], 'payments': []}

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def add_lead(name, phone, source='site', lang='ru'):
    db = load_db()
    entry = {
        'type': 'lead',
        'name': name,
        'phone': phone,
        'source': source,
        'lang': lang,
        'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'timestamp': datetime.now().isoformat()
    }
    db['leads'].append(entry)
    save_db(db)
    return entry

def add_payment(name, phone, plan, method, lang='ru'):
    db = load_db()
    prices = {'good': 19900, 'great': 39900, 'mentor': 89900}
    plan_names = {
        'good':   {'ru': 'Хороший',       'kz': 'Жақсы'},
        'great':  {'ru': 'Отличный',      'kz': 'Керемет'},
        'mentor': {'ru': 'Наставничество','kz': 'Тәлімгерлік'}
    }
    entry = {
        'type': 'payment',
        'name': name,
        'phone': phone,
        'plan': plan,
        'plan_name': plan_names.get(plan, {}).get('ru', plan),
        'price': prices.get(plan, 0),
        'method': method,
        'lang': lang,
        'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'timestamp': datetime.now().isoformat()
    }
    db['payments'].append(entry)
    save_db(db)
    return entry

# ══ ФОРМАТИРОВАНИЕ СООБЩЕНИЙ ══
def format_lead_msg(data):
    return (
        f"🎁 <b>НОВЫЙ ЛИД — БЕСПЛАТНЫЙ УРОК</b>\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Контакт: {data['phone']}\n"
        f"🌐 Язык: {'🇷🇺 Русский' if data.get('lang')=='ru' else '🇰🇿 Қазақша'}\n"
        f"📍 Источник: {data.get('source','сайт')}\n"
        f"🕐 Время: {data['time']} (Алматы)\n\n"
        f"➡️ Свяжись в течение 5 минут!"
    )

def format_payment_msg(data):
    method_icons = {
        'kaspi': '🟠 Kaspi Pay',
        'card':  '💳 Банковская карта',
        'tg':    '📨 Telegram'
    }
    return (
        f"💰 <b>НОВАЯ ЗАЯВКА НА ОПЛАТУ!</b>\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Контакт: {data['phone']}\n"
        f"📦 Тариф: {data['plan_name']} — {data['price']:,} ₸\n"
        f"💳 Способ: {method_icons.get(data['method'], data['method'])}\n"
        f"🌐 Язык: {'🇷🇺 Русский' if data.get('lang')=='ru' else '🇰🇿 Қазақша'}\n"
        f"🕐 Время: {data['time']} (Алматы)\n\n"
        f"🔥 Отправь ссылку на оплату как можно скорее!"
    )

# ══ КОМАНДЫ БОТА ══
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    if str(msg.chat.id) != str(ADMIN_ID):
        bot.send_message(msg.chat.id, "⛔ Нет доступа.")
        return
    bot.send_message(msg.chat.id,
        "👋 <b>Dias TargetPro — Бот уведомлений</b>\n\n"
        "Я буду присылать тебе сообщение каждый раз когда:\n"
        "• 🎁 Кто-то оставит заявку на бесплатный урок\n"
        "• 💰 Кто-то захочет купить курс\n\n"
        "<b>Команды:</b>\n"
        "/stats — Статистика за всё время\n"
        "/today — Заявки за сегодня\n"
        "/leads — Последние 10 лидов\n"
        "/payments — Последние 10 оплат\n"
        "/export — Экспорт всех данных\n"
        "/help — Помощь",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    if str(msg.chat.id) != str(ADMIN_ID): return
    db = load_db()
    leads = db.get('leads', [])
    payments = db.get('payments', [])
    total_rev = sum(p.get('price', 0) for p in payments)
    
    plan_counts = defaultdict(int)
    for p in payments:
        plan_counts[p.get('plan_name', '?')] += 1
    
    lang_leads = defaultdict(int)
    for l in leads:
        lang_leads[l.get('lang', 'ru')] += 1

    plan_txt = '\n'.join([f"  • {k}: {v} чел." for k, v in plan_counts.items()]) or '  Нет данных'
    
    bot.send_message(msg.chat.id,
        f"📊 <b>СТАТИСТИКА ЗА ВСЁ ВРЕМЯ</b>\n\n"
        f"🎁 Лидов (бесплатный урок): <b>{len(leads)}</b>\n"
        f"💰 Заявок на оплату: <b>{len(payments)}</b>\n"
        f"💵 Потенциальный доход: <b>{total_rev:,} ₸</b>\n\n"
        f"📦 По тарифам:\n{plan_txt}\n\n"
        f"🌐 По языку (лиды):\n"
        f"  🇷🇺 Русский: {lang_leads.get('ru',0)}\n"
        f"  🇰🇿 Казахский: {lang_leads.get('kz',0)}",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['today'])
def cmd_today(msg):
    if str(msg.chat.id) != str(ADMIN_ID): return
    db = load_db()
    today = datetime.now().strftime('%d.%m.%Y')
    
    today_leads = [l for l in db.get('leads', []) if l.get('time','').startswith(today)]
    today_pays  = [p for p in db.get('payments', []) if p.get('time','').startswith(today)]
    
    if not today_leads and not today_pays:
        bot.send_message(msg.chat.id, f"📅 Сегодня ({today}) заявок пока нет.")
        return
    
    text = f"📅 <b>СЕГОДНЯ ({today})</b>\n\n"
    if today_leads:
        text += f"🎁 Лидов: {len(today_leads)}\n"
        for l in today_leads[-5:]:
            text += f"  • {l['name']} | {l['phone']} | {l['time'][-5:]}\n"
    if today_pays:
        text += f"\n💰 Заявок на оплату: {len(today_pays)}\n"
        for p in today_pays[-5:]:
            text += f"  • {p['name']} | {p['plan_name']} | {p['price']:,}₸ | {p['time'][-5:]}\n"
    
    bot.send_message(msg.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['leads'])
def cmd_leads(msg):
    if str(msg.chat.id) != str(ADMIN_ID): return
    db = load_db()
    leads = db.get('leads', [])[-10:]
    if not leads:
        bot.send_message(msg.chat.id, "🎁 Лидов пока нет.")
        return
    text = f"🎁 <b>ПОСЛЕДНИЕ {len(leads)} ЛИДОВ</b>\n\n"
    for i, l in enumerate(reversed(leads), 1):
        flag = '🇷🇺' if l.get('lang') == 'ru' else '🇰🇿'
        text += f"{i}. {flag} <b>{l['name']}</b>\n   📱 {l['phone']} | 🕐 {l['time']}\n\n"
    bot.send_message(msg.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['payments'])
def cmd_payments(msg):
    if str(msg.chat.id) != str(ADMIN_ID): return
    db = load_db()
    pays = db.get('payments', [])[-10:]
    if not pays:
        bot.send_message(msg.chat.id, "💰 Заявок на оплату пока нет.")
        return
    text = f"💰 <b>ПОСЛЕДНИЕ {len(pays)} ЗАЯВОК</b>\n\n"
    for i, p in enumerate(reversed(pays), 1):
        flag = '🇷🇺' if p.get('lang') == 'ru' else '🇰🇿'
        text += (f"{i}. {flag} <b>{p['name']}</b>\n"
                 f"   📦 {p['plan_name']} — {p['price']:,} ₸\n"
                 f"   📱 {p['phone']} | 🕐 {p['time']}\n\n")
    bot.send_message(msg.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['export'])
def cmd_export(msg):
    if str(msg.chat.id) != str(ADMIN_ID): return
    db = load_db()
    
    # CSV для Google Sheets
    lines = ['Тип,Имя,Телефон,Тариф,Сумма,Способ оплаты,Язык,Время']
    for l in db.get('leads', []):
        lines.append(f"Лид,{l['name']},{l['phone']},,,,{l.get('lang','ru')},{l['time']}")
    for p in db.get('payments', []):
        lines.append(f"Оплата,{p['name']},{p['phone']},{p['plan_name']},{p['price']},{p.get('method','')},{p.get('lang','ru')},{p['time']}")
    
    csv_content = '\n'.join(lines)
    fname = f"leads_{datetime.now().strftime('%d%m%Y')}.csv"
    with open(fname, 'w', encoding='utf-8-sig') as f:
        f.write(csv_content)
    
    with open(fname, 'rb') as f:
        bot.send_document(msg.chat.id, f, caption=f"📊 Экспорт данных на {datetime.now().strftime('%d.%m.%Y')}")
    os.remove(fname)

@bot.message_handler(commands=['help'])
def cmd_help(msg):
    if str(msg.chat.id) != str(ADMIN_ID): return
    bot.send_message(msg.chat.id,
        "ℹ️ <b>ПОМОЩЬ</b>\n\n"
        "Этот бот автоматически получает уведомления с твоего сайта.\n\n"
        "<b>Что нужно сделать:</b>\n"
        "1. Вставь BOT_TOKEN и ADMIN_ID в этот файл\n"
        "2. Вставь токен и chat_id в сайт (dias_landing.html)\n"
        "3. Запусти: python dias_bot.py\n\n"
        "<b>Команды:</b>\n"
        "/stats — Полная статистика\n"
        "/today — Заявки за сегодня\n"
        "/leads — Последние лиды\n"
        "/payments — Последние оплаты\n"
        "/export — Скачать CSV файл",
        parse_mode='HTML'
    )

# Обработка неизвестных команд
@bot.message_handler(func=lambda m: True)
def unknown(msg):
    if str(msg.chat.id) == str(ADMIN_ID):
        bot.send_message(msg.chat.id, "Используй /help для списка команд.")

if __name__ == '__main__':
    print("=" * 55)
    print("  DIAS TARGETPRO BOT — ЗАПУЩЕН")
    print("=" * 55)
    if BOT_TOKEN == 'ВАШ_БОТ_ТОКЕН_ЗДЕСЬ':
        print("\n⚠️  ВНИМАНИЕ: Замени BOT_TOKEN и ADMIN_ID!")
        print("   Инструкция в начале файла (читай комментарии)")
    else:
        print(f"\n✅ Бот запущен. Жду уведомлений с сайта...")
        print(f"   Admin ID: {ADMIN_ID}")
    print("\nНажми Ctrl+C для остановки\n")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
