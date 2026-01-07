import requests

def getChatGPTanswer(text):
    # Processing the text input
    words = text.split()
    if len(words) > 0:
        words.pop(0)
    prompt = " ".join(words)

    # Call Ollama API
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama2',
        'prompt': prompt,
        'stream': False
    })

    if response.status_code == 200:
        data = response.json()
        return data.get('response', 'No response from Ollama')
    else:
        return f'Error: {response.status_code} - {response.text}'
