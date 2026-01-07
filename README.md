# Telegram Finance Tracker Bot

A Telegram bot for tracking personal finances, viewing spending statistics, and managing expenses.

## Features

- **Finance Tracking**: Record and categorize daily expenses
- **Statistics View**: Check spending by day, week, month, or year
- **Total Balance Check**: View current total money
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
   SPREADSHEET_ID = 'your-google-spreadsheet-id'
   API_KEY = 'your-telegram-bot-token'
   ```

   **Security Note**: Never commit `constants.py` to version control. Use environment variables instead:
   ```bash
   export SPREADSHEET_ID='your-id'
   export API_KEY='your-token'
   ```

## Setup

### Telegram Bot
1. Create a bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Set the token in `Utils/constants.py` as `API_KEY`

### Google Sheets
1. Create a Google Spreadsheet
2. Share it with your service account email (from the JSON file)
3. Get the spreadsheet ID from the URL
4. Place your service account JSON file in `Utils/` (ensure it's ignored in .gitignore)

## Testing

The project includes comprehensive unit and integration tests.

### Running Tests

1. Install test dependencies (included in requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```

2. Run all tests:
   ```bash
   python run_tests.py
   # or directly with pytest
   python -m pytest tests/ -v --cov=. --cov-report=term-missing
   ```

3. Run specific test categories:
   ```bash
   # Unit tests only
   python -m pytest tests/ -m "not integration"

   # Integration tests only
   python -m pytest tests/ -m integration

   # Tests with coverage report
   python -m pytest tests/ --cov=. --cov-report=html
   ```

### Test Coverage

The test suite covers:
- **Message Processing**: Input validation, command handling, error responses
- **Google Sheets Integration**: CRUD operations, error handling, data formatting
- **Data Processing**: Report generation, date handling, currency formatting
- **Integration Tests**: End-to-end workflows combining multiple components

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
docker run -e SPREADSHEET_ID='your-id' -e API_KEY='your-token' telebot
```

## Render Deployment

Deploy to Render for 24/7 hosting:

1. **Fork and Clone**: Fork this repository to your GitHub account

2. **Create Render Service**:
   - Go to [Render](https://render.com) and create a new account
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `telebot` (or your choice)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

3. **Set Environment Variables**:
   In Render dashboard, go to your service → Environment → Add Environment Variable:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
   - `SPREADSHEET_ID`: Your Google Spreadsheet ID
   - `OPENAI_API_KEY`: Your OpenAI API key (optional, for AI features)
   - `GOOGLE_CREDENTIALS_JSON`: The entire JSON content of your Google service account credentials file
   - `PORT`: Will be set automatically by Render

4. **Google Credentials**:
   - Get your Google service account JSON file content
   - Paste the entire JSON as the value for `GOOGLE_CREDENTIALS_JSON` environment variable
   - **Security**: Never commit credentials to Git

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your bot
   - Once deployed, your bot will be running 24/7

6. **Health Check**:
   - Visit `https://your-service-name.onrender.com/health` to verify the service is running
   - The bot will start automatically when the web service starts

## Project Structure

- `main.py`: Main bot logic and Telegram handlers
- `responses.py`: Message processing and responses
- `openAI.py`: Local Ollama integration for AI responses
- `spendings.py`: Spending tracking functionality
- `Utils/constants.py`: API keys and configuration (ignored)
- `Utils/myfinance1514-2-53f670e62850.json`: Google service account credentials (ignored)
- `tests/`: Comprehensive test suite
- `Dockerfile`: Docker configuration
- `requirements.txt`: Python dependencies
- `pytest.ini`: Test configuration
- `run_tests.py`: Test runner script

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.