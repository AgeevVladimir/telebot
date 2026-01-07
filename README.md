# Telegram Finance Tracker Bot

A Telegram bot for tracking personal finances, viewing spending statistics, and managing expenses with AI-powered responses.

## Features

- **Finance Tracking**: Record and categorize daily expenses
- **Statistics View**: Check spending by day, week, month, or year
- **Total Balance Check**: View current total money
<<<<<<< HEAD
- **AI Integration**: Get smart responses using local Ollama (free and private)
- **Google Sheets Integration**: Store data in a Google Spreadsheet
- **Persistent Keyboard**: Easy access to common functions

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd telebot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables or create `Utils/constants.py` with your API keys:
   ```python
   OPENAI_API_KEY = 'your-openai-api-key'
   SPREADSHEET_ID = 'your-google-spreadsheet-id'
   API_KEY = 'your-telegram-bot-token'
   ```

   **Security Note**: Never commit `constants.py` to version control. Use environment variables instead:
   ```bash
   export OPENAI_API_KEY='your-key'
   export SPREADSHEET_ID='your-id'
   export API_KEY='your-token'
   ```

## Setup

### Telegram Bot
1. Create a bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
<<<<<<< HEAD
3. Set the token in `Utils/constants.py` as `API_KEY`

### Google Sheets
1. Create a Google Spreadsheet
2. Share it with your service account email (from the JSON file)
3. Get the spreadsheet ID from the URL
4. Place your service account JSON file in `Utils/` (ensure it's ignored in .gitignore)

<<<<<<< HEAD
### Local AI (Ollama)
1. Install Ollama: `brew install ollama`
2. Start Ollama service: `brew services start ollama`
3. Pull a model: `ollama pull llama2`
4. The bot will use local AI for responses (no API keys needed!)

## Usage

1. Run the bot:
   ```bash
   python main.py
   ```

2. Start a chat with your bot on Telegram and send `/start`

3. Use the keyboard buttons to:
   - Check total balance
   - View spending statistics by time period
   - Record expenses by category
   - Get AI responses for queries

## Categories

Available spending categories:
- 🛒 Products
- 👶 Children
- 🚇 Transport
- 💊 Health
- 🍔 Food outside home
- 🏠 Rent
- 🎢 Entertainment
- 🎁 Gifts
- 👕 Shopping
- 🐈‍⬛ Cats
- 🏡 Repairs
- 🌐 Services
- 📚 Education
- ✈️ Travel
- 🌎 Other

## Docker Deployment

Build and run with Docker:
```bash
docker build -t telebot .
docker run -e OPENAI_API_KEY='your-key' -e SPREADSHEET_ID='your-id' -e API_KEY='your-token' telebot
```

## Project Structure

- `main.py`: Main bot logic and Telegram handlers
- `responses.py`: Message processing and responses
<<<<<<< HEAD
- `openAI.py`: Local Ollama integration for AI responses
- `spendings.py`: Spending tracking functionality
- `Utils/constants.py`: API keys and configuration (ignored)
- `Utils/myfinance1514-2-53f670e62850.json`: Google service account credentials (ignored)
- `Dockerfile`: Docker configuration
- `requirements.txt`: Python dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.