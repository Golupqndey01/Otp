from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7649519680:AAFO7LyIda7qQRmIwgI9WXSmRlWesqI2SK0"
ADMIN_ID = 7776174537  # 👈 yahan apna Telegram ID daalna                                                                                                 ADMIN_USERNAME = "SIDPANDEY02"  # 👈 admin ka username (@ ke bina)

# === Start Command ===                                                                                                                                   async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [    
        [InlineKeyboardButton("🇮🇳 India", callback_data="country:india")],
        [InlineKeyboardButton("🇺🇸 USA", callback_data="country:usa")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")]
    ]
    await update.message.reply_text("🌍 Please select your country:", reply_markup=InlineKeyboardMarkup(keyboard))

# === Country Selection ===                                                                                                                               async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    country = query.data.split(":")[1]
    context.user_data["country"] = country

    # Example numbers for country
    if country == "india":                                                                                                                                        keyboard = [
            [InlineKeyboardButton("📞 +91 9876543210 (₹50)", callback_data="number:+919876543210")],                                                                  [InlineKeyboardButton("📞 +91 9123456789 (₹60)", callback_data="number:+919123456789")]                                                               ]                                                                                                                                                     elif country == "usa":                                                                                                                                        keyboard = [                                                                                                                                                  [InlineKeyboardButton("📞 +1 5551234567 ($1)", callback_data="number:+15551234567")],
            [InlineKeyboardButton("📞 +1 5559876543 ($2)", callback_data="number:+15559876543")]
        ]
    else:
        keyboard = []

    await query.edit_message_text(f"✅ You selected {country}. Now choose a number:", reply_markup=InlineKeyboardMarkup(keyboard))

# === Number Selection ===
async def select_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    number = query.data.split(":")[1]
    context.user_data["number"] = number

    keyboard = [[InlineKeyboardButton("💰 Payment Done", callback_data="payment_done")]]
    await query.edit_message_text(f"📞 You selected number: {number}\n\nPlease make the payment payment UPI kumarsoni@fam and then click below:", reply_m>

# === Payment Done → Ask UTR ===
async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Please send your UTR / Transaction ID here:")

    context.user_data["awaiting_utr"] = True

# === Collect UTR from User ===
async def collect_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_utr"):
        utr = update.message.text
        country = context.user_data.get("country", "Unknown")
        number = context.user_data.get("number", "Unknown")

        # Save UTR
        context.user_data["utr"] = utr
        context.user_data["awaiting_utr"] = False

        # Notify user
        await update.message.reply_text("🙏 Thanks! Your payment request has been submitted. Wait for admin approval.")

        # Notify Admin
        admin_text = (
            f"💰 Payment Request Received\n"
            f"👤 User: @{update.message.from_user.username or 'NoUsername'} (ID: {update.message.from_user.id})\n"
            f"🌍 Country: {country}\n"
            f"📞 Number: {number}\n"
            f"🏷 UTR: {utr}\n\n"
            f"🔑 To send OTP:\n/sendotp {update.message.from_user.id} <otp>"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

# === Admin Sends OTP ===
async def send_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠ Usage: /sendotp <user_id> <otp>")
            return

        user_id = int(args[0])
        otp = args[1]

        await context.bot.send_message(chat_id=user_id, text=f"🔑 Your OTP is: {otp}")
        await update.message.reply_text(f"✅ OTP sent to user {user_id}: {otp}")

    except Exception as e:
        await update.message.reply_text(f"⚠ Error: {e}")

# === Contact Admin (Button Click) ===
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("📞 Chat with Admin", url=f"https://t.me/{ADMIN_USERNAME}")]]
    await query.edit_message_text(
        "Aap directly admin se baat kar sakte ho 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# === Main ===
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sendotp", send_otp))
    application.add_handler(CallbackQueryHandler(select_country, pattern="^country:"))
    application.add_handler(CallbackQueryHandler(select_number, pattern="^number:"))
    application.add_handler(CallbackQueryHandler(payment_done, pattern="^payment_done$"))
    application.add_handler(CallbackQueryHandler(contact_admin, pattern="^contact_admin$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_utr))

    # Menu Button
    commands = [
        BotCommand("start", "Start / Select Country"),
        BotCommand("sendotp", "Send OTP (Admin Only)")
    ]
    async def post_init(app): await app.bot.set_my_commands(commands)
    application.post_init = post_init

    print("🤖 Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
