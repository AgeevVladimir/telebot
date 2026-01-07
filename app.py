from flask import Flask
import threading
import main  # Import the bot module

app = Flask(__name__)

@app.route('/')
def home():
    return 'Telegram Bot is running!'

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=main.run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=10000)