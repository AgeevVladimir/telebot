import random
from datetime import datetime

from requests import *

import openAI
import spendings


def sample_responses(input_text):
    user_message = str(input_text).lower()

    if user_message in ("hi", "hello"):
        return "Hey! How is it going?"

    if user_message in "who are you":
        return "I'm MyFinance1514_bot"

    if user_message in "time":
        now = datetime.now()
        date_time = now.strftime("%d/%m/%y, %H:%M:%S")
        return str(date_time)

    if user_message in "number":
        num = random.randint(0, 100)
        adress = 'http://numbersapi.com/' + str(num)
        response = get(adress).text
        return response

    # Handle sum and category

    if user_message[0].isdigit():
        return spendings.saveSpending(user_message)

    # Подключение к ChatGPT

    if user_message.startswith("chatgpt"):
        return openAI.getChatGPTanswer(user_message)

    return "I don't understand you"
