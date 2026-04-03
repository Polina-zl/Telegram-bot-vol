import telebot
from config import TOKEN
from extensions import APIException, CryptoConverter

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_instructions(message):
    instructions = (
        "Привет! Я покажу цену одной валюты в другой.\n\n"
        "Введи сообщение в формате:\n"
        "<исходная валюта> <целевая валюта> <количество>\n\n"
        "Пример: USD EUR 100\n\n"
        "Доступные валюты: USD, EUR, RUB\n\n"
        "Команды:\n"
        "/values — список доступных валют\n"
        "/help — эта инструкция"
    )
    bot.reply_to(message, instructions)


@bot.message_handler(commands=['values'])
def show_currencies(message):
    text = "Доступные валюты:\n- USD (доллар)\n- EUR (евро)\n- RUB (рубль)"
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def handle_conversion(message):
    user_text = message.text.strip()
    parts = user_text.split()

    if len(parts) != 3:
        bot.reply_to(message, "Ошибка: нужно 3 аргумента. Пример: USD EUR 100")
        return

    base, quote, amount = parts[0], parts[1], parts[2]

    try:
        total = CryptoConverter.get_price(base, quote, amount)
        bot.reply_to(message, f"Цена {amount} {base.upper()} в {quote.upper()} = {total} {quote.upper()}")
    except APIException as e:
        bot.reply_to(message, f"Ошибка: {e}")
    except Exception as e:
        bot.reply_to(message, f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)