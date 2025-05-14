import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)
import openai
import os



# Settings, Tokens and API-KEYS
TELEGRAM_TOKEN = "Create"
OPENAI_API_KEY = "Create"

openai.api_key = OPENAI_API_KEY

#Communication Stages
ASK_PASSPORT, ASK_CAR_DOC, CONFIRM_DATA = range(3)

#Temporary data storage
user_data_store = {}

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Fake Photo Analysis
def fake_mindee_parser(photo_path: str) -> dict | None:
    # Simulation of image analysis
    if "bad" in photo_path:
        return None
    return {
        "full_name": "John Doe",
        "passport_number": "X1234567",
        "car_model": "Toyota Camry",
        "vin": "123ABC456XYZ"
    }

#OpenAI Respound
async def ai_response(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Sorry, something went wrong with the AI response."

#/start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " Hello! I’m your assistant for purchasing car insurance.\n"
        "Please send a photo of your *passport* to begin.",
        parse_mode="Markdown"
    )
    return ASK_PASSPORT

#Passport photo recieve
async def receive_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Please send a photo, not text.")
        return ASK_PASSPORT

    photo = await update.message.photo[-1].get_file()
    passport_path = f"passport_{update.message.from_user.id}.jpg"
    await photo.download_to_drive(passport_path)
    context.user_data["passport_photo"] = passport_path

    await update.message.reply_text("Passport received. Now send your *car document* photo.")
    return ASK_CAR_DOC

#Car Document photo recieve
async def receive_car_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Please send a photo, not text.")
        return ASK_CAR_DOC

    photo = await update.message.photo[-1].get_file()
    car_doc_path = f"cardoc_{update.message.from_user.id}.jpg"
    await photo.download_to_drive(car_doc_path)
    context.user_data["car_doc"] = car_doc_path

    #Mindee API Simulation
    extracted_data = fake_mindee_parser(passport_path := context.user_data["passport_photo"])
    if not extracted_data:
        await update.message.reply_text("Unable to extract data from the passport image. Please resend it.")
        return ASK_PASSPORT

    extracted_data.update(fake_mindee_parser(car_doc_path) or {})

    context.user_data["extracted_data"] = extracted_data

    info = "\n".join([f"*{key.replace('_', ' ').title()}:* {value}" for key, value in extracted_data.items()])
    await update.message.reply_text(
        f" Here is the extracted data:\n{info}\n\nIs this correct? (yes/no)",
        parse_mode="Markdown"
    )
    return CONFIRM_DATA

# Data Confirmation
async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == "yes" and "price_confirmed" not in context.user_data:
        context.user_data["price_confirmed"] = True
        await update.message.reply_text("Great! The price for insurance is *100 USD*. Do you agree? (yes/no)", parse_mode="Markdown")
        return CONFIRM_DATA

    elif text == "yes" and context.user_data.get("price_confirmed"):
        await update.message.reply_text("Generating insurance policy...")

        dummy_policy = (
            " *Your Insurance Policy*\n"
            f"Name: {context.user_data['extracted_data'].get('full_name')}\n"
            f"Car: {context.user_data['extracted_data'].get('car_model')}\n"
            f"VIN: {context.user_data['extracted_data'].get('vin')}\n"
            f"Policy Number: POL-{update.message.from_user.id}-001\n"
            f"Price: 100 USD\n"
        )
        await update.message.reply_text(dummy_policy, parse_mode="Markdown")
        await update.message.reply_text("Thank you! Your policy is ready.")
        return ConversationHandler.END

    elif text == "no" and context.user_data.get("price_confirmed"):
        await update.message.reply_text("Sorry, the price is fixed and cannot be changed.")
        return ConversationHandler.END

    elif text == "no":
        await update.message.reply_text("Please re-send a *passport photo*.")
        return ASK_PASSPORT

    else:
        await update.message.reply_text("I didn't understand. Please answer 'yes' or 'no'.")
        return CONFIRM_DATA

#Error Handling
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again.")

#"Cancel" Command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process cancelled. Type /start to begin again.")
    return ConversationHandler.END

# MAIN Function
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PASSPORT: [MessageHandler(filters.PHOTO, receive_passport),
                           MessageHandler(filters.TEXT, receive_passport)],
            ASK_CAR_DOC: [MessageHandler(filters.PHOTO, receive_car_doc),
                          MessageHandler(filters.TEXT, receive_car_doc)],
            CONFIRM_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_data)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
