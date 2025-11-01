# Test Suite for Project Samarth
import unittest
import asyncio
from samarth.services.llm_service import LLMService
from samarth.utils.validation import validate_query, sanitize_input

class TestDatasetManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.llm_service = LLMService()
    
    def test_identify_relevant_datasets_agriculture(self):
        """Test that agricultural questions identify agriculture datasets"""
        question = "What is the crop production in Punjab?"
        # Run the method on the LLMService instance
        datasets = self.llm_service.identify_relevant_datasets(question)
        self.assertIn("agricultural_production", datasets)
        
    def test_identify_relevant_datasets_climate(self):
        """Test that climate questions identify climate datasets"""
        question = "What was the rainfall in Mumbai last month?"
        # Run the method on the LLMService instance
        datasets = self.llm_service.identify_relevant_datasets(question)
        self.assertIn("weather_data", datasets)
        
    def test_identify_relevant_datasets_mixed(self):
        """Test that mixed questions identify multiple datasets"""
        question = "How does temperature affect wheat production?"
        # Run the method on the LLMService instance
        datasets = self.llm_service.identify_relevant_datasets(question)
        self.assertIn("weather_data", datasets)
        self.assertIn("agricultural_production", datasets)

class TestValidation(unittest.TestCase):
    def test_validate_safe_query(self):
        """Test that safe SELECT queries are validated correctly"""
        query = "SELECT * FROM agricultural_production WHERE state = 'Punjab'"
        is_valid, error = validate_query(query)
        self.assertTrue(is_valid)
        
    def test_validate_dangerous_query(self):
        """Test that dangerous queries are rejected"""
        query = "DROP TABLE agricultural_production"
        is_valid, error = validate_query(query)
        self.assertFalse(is_valid)
        self.assertIn("DROP", error)
        
    def test_validate_non_select_query(self):
        """Test that non-SELECT queries are rejected"""
        query = "UPDATE agricultural_production SET yield = 100"
        is_valid, error = validate_query(query)
        self.assertFalse(is_valid)
        self.assertIn("SELECT", error)

class TestSanitization(unittest.TestCase):
    def test_sanitize_input(self):
        """Test that input sanitization works correctly"""
        dirty_input = "SELECT *; DROP TABLE users;"
        clean_input = sanitize_input(dirty_input)
        self.assertNotIn(";", clean_input)
        self.assertNotIn("'", clean_input)

# Add a new test for the new data access method
class TestDataAccess(unittest.TestCase):
    def test_get_production_by_state_and_year_range(self):
        """Test the new method for getting production data by state and year range"""
        # This is a simple test that just verifies the method exists
        # In a real test environment, we would mock the database connection
        from samarth.data.data_access import AgriculturalDataAccess
        self.assertTrue(hasattr(AgriculturalDataAccess, 'get_production_by_state_and_year_range'))

if __name__ == '__main__':
    unittest.main()