
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = '8345909851:AAHZk6XnT_BsN3Ugo2JErcvWHBDmxfsUEzg'
AI_MODEL_API_URL = 'YOUR_AI_MODEL_API_ENDPOINT'
AI_MODEL_API_KEY = 'YOUR_AI_MODEL_API_KEY'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! I am an AI-powered bot. Send me a message, and I will try to respond intelligently.')

def get_ai_response(user_message: str) -> str:
    headers = {
        'Authorization': f'Bearer {AI_MODEL_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': user_message
    }
    try:
        response = requests.post(AI_MODEL_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('choices')[0].get('text').strip()
    except requests.exceptions.RequestException as e:
        print(f"Error calling AI model API: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now."



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    ai_response = get_ai_response(user_message)
    await update.message.reply_text(ai_response)

def main() -> None:

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()