import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ⚠️ نصيحة أمنية: لا تشارك التوكن الخاص بك علناً، يفضل تغييره من BotFather إذا شافه شخص غيرك
BOT_TOKEN = '827607751:AAFrSAdzEFkr0y5tobjlZcKvvo0arEoAAKo'
OWNER_ID = 8571901492 

bot = telebot.TeleBot(BOT_TOKEN)

message_user_map = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    استقبال أمر /start
    """
    if message.chat.id == OWNER_ID:
        bot.send_message(OWNER_ID, "مرحباً سيدي المالك 👑. البوت يعمل وجاهز لاستقبال الرسائل (نصوص ووسائط).")
        return

    welcome_text = """
مرحبا بك 👋

أرسل رسالتك (نص، صورة، فيديو، ملف، أو بصمة صوت) 📩 ، 
وسيتم الرد عليك في أسرع وقت ⏳ .
"""
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

# إضافة دعم كل أنواع الوسائط لردود المالك
@bot.message_handler(func=lambda message: message.chat.id == OWNER_ID, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'video_note'])
def handle_owner_reply(message):
    """
    استقبال ردود المالك وإرسالها للمستخدم (نصوص أو وسائط)
    """
    if message.reply_to_message:
        owner_msg_id = message.reply_to_message.message_id
        user_id = message_user_map.get(owner_msg_id)
        
        if user_id:
            try:
                # إذا كان الرد نص عادي
                if message.content_type == 'text':
                    bot.send_message(user_id, f"{message.text}", parse_mode='Markdown')
                else:
                    # إذا كان الرد صورة، فيديو، أو ملف (يتم إرسال تنبيه ثم نسخ الوسائط)
                    bot.copy_message(user_id, OWNER_ID, message.message_id)
                
                bot.reply_to(message, "✅ تم إرسال ردك للمستخدم بنجاح.")
            except Exception as e:
                bot.reply_to(message, f"❌ حدث خطأ، ربما قام المستخدم بحظر البوت: {e}")
        else:
            bot.reply_to(message, "⚠️ لم أتمكن من العثور على المستخدم. ربما تم إعادة تشغيل البوت أو أن الرسالة قديمة جداً.")
    else:
        bot.reply_to(message, "💡 للرد على مستخدم، اضغط على رسالته (أو الصورة/الملف) واختر (Reply / رد) ثم أرسل ردك.")

# إضافة دعم كل أنواع الوسائط لرسائل المستخدمين
@bot.message_handler(func=lambda message: message.chat.id != OWNER_ID, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'video_note'])
def handle_user_message(message):
    """
    استقبال رسائل المستخدمين وإرسالها للمالك
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    user_info_card = f"""
👤 *بيانات المرسل:*
━━━━━━━━━━━━
🏷️ *الاسم:* {first_name}
🆔 *المعرف:* `{user_id}`
━━━━━━━━━━━━
    """
    
    markup = InlineKeyboardMarkup()
    if username:
        btn = InlineKeyboardButton(text=f"فتح حساب {first_name} 🔗", url=f"https://t.me/{username}")
        markup.add(btn)
    else:
        btn = InlineKeyboardButton(text="لا يوجد يوزرنيم 🚫", callback_data="no_username")
        markup.add(btn)

    try:
        # إذا كانت الرسالة نصية، نستخدم التنسيق القديم
        if message.content_type == 'text':
            content_text = f"📩 *رسالة جديدة من مستخدم*\n━━━━━━━━━━━━\n💬 *الرسالة:*\n{message.text}"
            sent_msg = bot.send_message(OWNER_ID, content_text, parse_mode='Markdown')
        else:
            # إذا كانت صورة، فيديو، أو ملف، نستخدم دالة النسخ لترسلها مثل ما هي
            sent_msg = bot.copy_message(OWNER_ID, message.chat.id, message.message_id)
        
        # ربط الـ ID حتى تقدر ترد عليها
        message_user_map[sent_msg.message_id] = user_id
        
        # إرسال كارت معلومات المستخدم مباشرة تحت الرسالة أو الصورة
        bot.send_message(OWNER_ID, user_info_card, parse_mode='Markdown', reply_markup=markup)
        
        bot.reply_to(message, "تم استلام رسالتك وسيتم الرد عليك قريبًا ✅")
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال الرسالة للمالك: {e}")

if __name__ == '__main__':
    print("البوت يعمل ومستعد لاستقبال كافة أنواع الوسائط...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
