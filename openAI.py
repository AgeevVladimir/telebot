from openai import OpenAI

from Utils import constants


def getChatGPTanswer(text):
    client = OpenAI(api_key=constants.OPENAI_API_KEY)
    # Processing the text input
    words = text.split()
    if len(words) > 0:
        words.pop(0)
    text_for_chatgpt = " ".join(words)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": text_for_chatgpt}
        ]
    )

    generated_text = response.choices[0].text.strip()
    return generated_text
