from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import pandas as pd
import os

# توكن البوت ومعرف المالك
BOT_TOKEN = "توكنك"
OWNER_ID = ايديك  # ضع ايديك هنا

excel_data = {}
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("بحث 📲", callback_data="search_zain")],
        [
            InlineKeyboardButton(" ݂⭒ ֺ۪ قناة البوت   ֺ۪ ⭒ ݂", url="https://t.me/dev_DATAIRAQ"),
            InlineKeyboardButton(" ݂⭒ ֺ۪  المبرمج  ֺ۪ ⭒ ݂", url="https://t.me/U_9_9U"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = (
        f"• أهلاً بك {user_name} بوت قاعدة بيانات 🌐\n\n"
        "• بيانات لـ غرفه بيانات عـن الأرقام🧚‍♀️\n"
        "• أكبر منظمة بيانات عملاء 🌎\n"
        "تتضمن البيانات : محافظه - مدينه - قريه - سكن - ول مزيد\n"
        "==========================\n"
        "• مبرمج البوت: @dev_DATAIRAQ 👤\n"
        "• قناة البوت: @U_9_9U ⚠️\n"
        "=========================="
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⚠️ هذا الأمر متاح فقط للمالك.")
        return

    await update.message.reply_text("📤 أرسل ملف قاعدة البيانات (Excel):")
    context.user_data["awaiting_file"] = True

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_file" in context.user_data and context.user_data["awaiting_file"]:
        context.user_data["awaiting_file"] = False

       
        if not update.message.document.file_name.endswith(".xlsx"):
            await update.message.reply_text("⚠️ يرجى إرسال ملف بصيغة Excel (xlsx) فقط")
            return

    
        file = await update.message.document.get_file()
        file_path = f"database_{update.message.document.file_name}"
        await file.download_to_drive(file_path)

        try:
           
            excel_data.clear()
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                excel_data[sheet_name] = xls.parse(sheet_name)
            
            os.remove(file_path)
            await update.message.reply_text("✅ تم رفع قاعدة البيانات بنجاح")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ أثناء معالجة الملف: {e}")
    else:
        await update.message.reply_text("⚠️ لم يتم طلب رفع ملف")

async def search_zain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    await query.message.reply_text("🔍 أرسل الرقم الذي تريد البحث عنه (بدون رمز الدولة):")
    context.user_data["awaiting_number"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_number" in context.user_data and context.user_data["awaiting_number"]:
        number = update.message.text.strip()
        context.user_data["awaiting_number"] = False

       
        number = ''.join(filter(str.isdigit, number))

       
        results = []
        for sheet_name, sheet_data in excel_data.items():
           
            if "Unnamed: 6" in sheet_data.columns:
               
                matches = sheet_data[sheet_data["Unnamed: 6"].astype(str).str.contains(number, na=False)]
                if not matches.empty:
                   
                    formatted_result = f"📁 البيانات من الملف: {sheet_name}\n"
                    for _, row in matches.iterrows():
                        row_data = "\n".join([f"📌 {col}: {value}" for col, value in row.items() if pd.notna(value)])
                        formatted_result += f"{row_data}\n{'-' * 30}\n"
                    results.append(formatted_result)

       
        if results:
            full_text = "📋 نتائج البحث:\n" + "\n\n".join(results)
            for part in split_message(full_text):
                await update.message.reply_text(part)
        else:
            await update.message.reply_text("❌ الرقم غير موجود في قاعدة البيانات.")
    else:
        await update.message.reply_text("⚠️ لم يتم طلب أي عملية بحث")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("upload", upload))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(CallbackQueryHandler(search_zain, pattern="search_zain"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 البوت شغال الآن...")
app.run_polling()
