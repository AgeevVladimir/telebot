import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import responses
import spendings


class TestResponses:
    """Test cases for message processing in responses.py"""

    def test_sample_responses_empty_message(self):
        """Test handling of empty messages"""
        result = responses.sample_responses("")
        assert "Please send a valid text message" in result

    def test_sample_responses_whitespace_message(self):
        """Test handling of whitespace-only messages"""
        result = responses.sample_responses("   ")
        assert "Please send a non-empty message" in result

    def test_sample_responses_invalid_message_type(self):
        """Test handling of non-string messages"""
        result = responses.sample_responses(None)
        assert "Please send a valid text message" in result

    @patch('spendings.save_spending')
    def test_sample_responses_spending_input_valid(self, mock_save):
        """Test valid spending input processing"""
        mock_save.return_value = "Spending saved successfully"
        result = responses.sample_responses("10.50 coffee")
        mock_save.assert_called_once_with("10.50 coffee")
        assert "Spending saved successfully" in result

    @patch('spendings.save_spending')
    def test_sample_responses_spending_input_error(self, mock_save):
        """Test spending input with save error"""
        mock_save.side_effect = Exception("Save failed")
        result = responses.sample_responses("10.50 coffee")
        assert "Error saving spending" in result

    @patch('spendings.delete_last_spending')
    def test_sample_responses_cancel_command(self, mock_delete):
        """Test cancel command processing"""
        mock_delete.return_value = "Entry deleted"
        result = responses.sample_responses("❌ Отмена")
        mock_delete.assert_called_once()
        assert "Entry deleted" in result

    @patch('spendings.update_last_spending_category')
    def test_sample_responses_category_selection(self, mock_update):
        """Test category selection processing"""
        mock_update.return_value = "Category updated"
        result = responses.sample_responses("🛒 Продукты")
        mock_update.assert_called_once_with("🛒 Продукты")
        assert "Category updated" in result

    @patch('spendings.get_report')
    def test_sample_responses_report_request(self, mock_report):
        """Test report request processing"""
        mock_report.return_value = "Daily report generated"
        result = responses.sample_responses("📊 День")
        mock_report.assert_called_once_with("📊 День")
        assert "Daily report generated" in result

    @patch('spendings.get_total_amount')
    def test_sample_responses_total_request(self, mock_total):
        """Test total balance request processing"""
        mock_total.return_value = "€ 1000.00"
        result = responses.sample_responses("💰💰💰  Сколько у нас всего денег 💰💰💰")
        mock_total.assert_called_once()
        assert "€ 1000.00" in result

    def test_sample_responses_unrecognized_message(self):
        """Test unrecognized message handling"""
        result = responses.sample_responses("some random message")
        assert "I don't understand you" in result

    def test_sample_responses_unexpected_error(self):
        """Test unexpected error handling"""
        with patch('spendings.save_spending', side_effect=Exception("Unexpected")):
            result = responses.sample_responses("10.50 coffee")
            assert "Error saving spending" in result


class TestSpendings:
    """Test cases for Google Sheets operations in spendings.py"""

    @patch('spendings.get_sheet_service')
    def test_get_total_amount_success(self, mock_service):
        """Test successful total amount retrieval"""
        mock_sheet = Mock()
        mock_service.return_value = mock_sheet
        mock_sheet.values().get().execute.return_value = {'values': [['1234.56']]}

        result = spendings.get_total_amount()
        assert "€ 1234.56" in result

    @patch('spendings.get_sheet_service')
    def test_get_total_amount_no_values(self, mock_service):
        """Test total amount with no values"""
        mock_sheet = Mock()
        mock_service.return_value = mock_sheet
        mock_sheet.values().get().execute.return_value = {}

        result = spendings.get_total_amount()
        assert "€ 0.00" in result

    @patch('spendings.get_sheet_service')
    def test_save_spending_valid_input(self, mock_service):
        """Test saving valid spending"""
        mock_sheet = Mock()
        mock_service.return_value = mock_sheet

        result = spendings.save_spending("10.50 coffee")
        assert "Spending saved" in result
        mock_sheet.values().append.assert_called_once()

    def test_save_spending_invalid_amount(self):
        """Test saving with invalid amount"""
        result = spendings.save_spending("invalid coffee")
        assert "Invalid amount" in result

    def test_save_spending_missing_description(self):
        """Test saving with missing description"""
        result = spendings.save_spending("10.50")
        assert "Please provide both amount and description" in result

    @patch('spendings.get_sheet_service')
    @patch('spendings.load_data_from_google_sheets')
    def test_get_report_daily(self, mock_load, mock_service):
        """Test daily report generation"""
        import pandas as pd

        # Mock dataframe
        mock_df = pd.DataFrame({
            'date': [datetime.now()],
            'category': ['Test'],
            'sum': [10.50],
            'comment': ['coffee'],
            'month': ['01 january'],
            'year': ['2026']
        })
        mock_load.return_value = mock_df

        result = spendings.get_report("📊 День")
        assert "Test" in result
        assert "10.5" in result

    @patch('spendings.get_sheet_service')
    def test_update_last_spending_category_success(self, mock_service):
        """Test successful category update"""
        mock_sheet = Mock()
        mock_service.return_value = mock_sheet
        mock_sheet.values().get().execute.return_value = {'values': [['header'], ['data']]}

        result = spendings.update_last_spending_category("🛒 Продукты")
        assert "Category updated" in result

    def test_update_last_spending_category_empty_text(self):
        """Test category update with empty text"""
        result = spendings.update_last_spending_category("")
        assert "Please provide a valid category" in result

    @patch('spendings.get_sheet_service')
    def test_delete_last_spending_success(self, mock_service):
        """Test successful spending deletion"""
        mock_sheet = Mock()
        mock_service.return_value = mock_sheet
        mock_sheet.values().get().execute.return_value = {'values': [['header'], ['data']]}

        result = spendings.delete_last_spending()
        assert "deleted successfully" in result

    @patch('spendings.get_sheet_service')
    def test_delete_last_spending_no_entries(self, mock_service):
        """Test deletion when no entries exist"""
        mock_sheet = Mock()
        mock_service.return_value = mock_sheet
        mock_sheet.values().get().execute.return_value = {'values': [['header']]}

        result = spendings.delete_last_spending()
        assert "No spending entries to delete" in result

    def test_get_current_date(self):
        """Test current date retrieval"""
        result = spendings.get_current_date()
        assert 'day' in result
        assert 'month' in result
        assert 'year' in result
        assert result['year'] == '2026'  # Based on context

    def test_get_day_abbreviation(self):
        """Test day abbreviation function"""
        assert spendings.get_day_abbreviation('Monday') == 'пн'
        assert spendings.get_day_abbreviation('Invalid') == 'Invalid'


class TestIntegration:
    """Integration tests combining multiple components"""

    @patch('spendings.save_spending')
    @patch('spendings.get_sheet_service')
    def test_full_spending_workflow(self, mock_service, mock_save):
        """Test complete spending workflow"""
        mock_save.return_value = "Spending saved. Don't forget to choose Category"

        # Simulate user input
        result = responses.sample_responses("25.99 groceries")
        assert "Spending saved" in result

        # Simulate category selection
        with patch('spendings.update_last_spending_category') as mock_update:
            mock_update.return_value = "Category updated"
            result = responses.sample_responses("🛒 Продукты")
            assert "Category updated" in result

    def test_error_propagation(self):
        """Test error handling across components"""
        with patch('spendings.save_spending', side_effect=Exception("DB Error")):
            result = responses.sample_responses("10.50 coffee")
            assert "Error saving spending" in result


if __name__ == "__main__":
    pytest.main([__file__])