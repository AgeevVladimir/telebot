import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_google_sheets_service():
    """Mock Google Sheets service for testing"""
    mock_service = Mock()
    mock_sheet = Mock()
    mock_service.return_value = mock_sheet

    # Mock the values operations
    mock_values = Mock()
    mock_sheet.values.return_value = mock_values
    mock_get = Mock()
    mock_values.get.return_value = mock_get
    mock_get.execute.return_value = {'values': [['header'], ['2026', '01 january', '2026-01-07 10:00:00', '10.50', 'coffee', '']]}

    return mock_service


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response"""
    return {
        'response': 'This is a mock AI response for testing purposes.'
    }


@pytest.fixture
def sample_spending_data():
    """Sample spending data for testing"""
    return [
        ['year', 'month', 'date', 'sum', 'comment', 'category'],
        ['2026', '01 january', '2026-01-07 09:00:00', '15.99', 'breakfast', '🛒 Продукты'],
        ['2026', '01 january', '2026-01-07 12:00:00', '8.50', 'coffee', '🍔 Еда вне дома'],
        ['2026', '01 january', '2026-01-06 18:00:00', '25.00', 'groceries', '🛒 Продукты']
    ]


@pytest.fixture(autouse=True)
def mock_constants():
    """Mock constants to avoid dependency on actual config files"""
    with patch('Utils.constants') as mock_consts:
        mock_consts.SPREADSHEET_ID = 'test_spreadsheet_id'
        mock_consts.OPENAI_API_KEY = 'test_openai_key'
        mock_consts.API_KEY = 'test_telegram_key'
        yield mock_consts


@pytest.fixture
def mock_logger():
    """Mock logger to avoid actual logging in tests"""
    with patch('responses.logger') as mock_resp_logger, \
         patch('spendings.logger') as mock_spend_logger, \
         patch('openAI.logger') as mock_ai_logger:

        yield {
            'responses': mock_resp_logger,
            'spendings': mock_spend_logger,
            'openai': mock_ai_logger
        }