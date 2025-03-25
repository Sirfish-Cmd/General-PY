"""
Tests for the form automation module.
"""
import pytest
import sys
import os

# Add the src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.form_automation import FormAutomator
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_webdriver():
    """Fixture to mock the selenium webdriver."""
    with patch('src.form_automation.webdriver.Chrome') as mock_driver:
        instance = mock_driver.return_value
        instance.find_elements.return_value = []
        yield instance

@pytest.fixture
def form_automator():
    """Fixture to create a form automator with a mocked driver."""
    with patch('src.form_automation.webdriver.Chrome') as mock_driver:
        instance = mock_driver.return_value
        instance.find_elements.return_value = []
        automator = FormAutomator("https://example.com/form")
        automator.driver = instance
        yield automator

def test_init(mock_webdriver):
    """Test initialization of FormAutomator."""
    with patch('src.form_automation.Service'), \
         patch('src.form_automation.ChromeDriverManager'):
        automator = FormAutomator("https://example.com/form")
        assert automator.form_url == "https://example.com/form"
        assert automator.headless is False

def test_fill_text_fields(form_automator):
    """Test filling text fields."""
    # Mock text field elements
    mock_field1 = MagicMock()
    mock_field1.get_attribute.return_value = 'text'
    mock_field2 = MagicMock()
    mock_field2.get_attribute.return_value = 'email'
    
    form_automator.driver.find_elements.return_value = [mock_field1, mock_field2]
    
    form_automator.fill_text_fields("TestUser", 1)
    
    mock_field1.clear.assert_called_once()
    mock_field1.send_keys.assert_called_once()
    mock_field2.clear.assert_called_once()
    mock_field2.send_keys.assert_called_once()

def test_submit_form_success(form_automator):
    """Test successful form submission."""
    with patch('src.form_automation.WebDriverWait') as mock_wait:
        mock_wait.return_value.until.return_value = MagicMock()
        
        result = form_automator.submit_form()
        
        assert result is True
