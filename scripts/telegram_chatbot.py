import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction, ParseMode

TELEGRAM_BOT_TOKEN = 'TELEGRAM_TOKEN'

API_URL = "API_URL_TO_HIT"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def get_ai_response(user_message: str) -> str:

    headers = {'Content-Type': 'application/json'}
    payload = {'prompt': user_message}

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.post(API_URL, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()

                    generated_text = data.get("response", "I could not generate a response.")

                    sources = data.get("sources", [])

                    if sources:
                        sources_list = []
                        for source in sources:
                            file_name = source.get("file_name", "N/A")
                            score = source.get("score", "N/A")
                            sources_list.append(f'• {file_name} (Score: {score})')
                        
                        sources_markdown = "\n\n*Sources:*\n" + "\n".join(sources_list)
                        return generated_text + sources_markdown
                    
                    return generated_text

                else:
                    error_details = await response.text()
                    logger.error(f"API Error: Status {response.status} - {error_details}")
                    return f"Sorry, the backend server responded with an error (HTTP {response.status})."

        except aiohttp.ClientConnectorError as e:
            logger.error(f"AIOHTTP Connection Error: {e}")
            return "Sorry, I can't connect to the backend server."
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred while fetching the response."

# Telegram Command and Message Handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text(
        "Hi! I'm an Vajra ,How can i help you"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_message = update.message.text
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    ai_response = await get_ai_response(user_message)

    await update.message.reply_text(ai_response, parse_mode=ParseMode.MARKDOWN)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set! Exiting.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting, polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()
