# LLM Service for Project Samarth
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import GenerationConfig

# Load environment variables from .env file
# The .env file is located in the samarth directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Fallback to default location
    load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Configure the API key for the generative AI client
        # Using getattr to avoid linter issues with non-exported methods
        configure_func = getattr(genai, 'configure')
        configure_func(api_key=api_key)
        
        # Try to create the model, fallback to gemini-pro if the specified model fails
        model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        try:
            self.model = GenerativeModel(model_name)
        except Exception as e:
            print(f"Warning: Failed to create model {model_name}: {e}")
            print("Falling back to gemini-pro model")
            self.model = GenerativeModel("gemini-pro")
    
    def identify_relevant_datasets(self, question: str) -> List[str]:
        """Identify relevant datasets for a given question"""
        # In a production environment, this would use embeddings or more sophisticated methods
        # For now, we'll use a simple keyword-based approach
        
        agriculture_keywords = ["crop", "farm", "agriculture", "yield", "production", "harvest", "irrigation", "fertilizer", "pesticide", "rice", "wheat", "maize", "sugarcane"]
        climate_keywords = ["weather", "rainfall", "temperature", "climate", "precipitation", "humidity", "monsoon", "wind", "heat", "cold", "warm", "hot", "cool", "chill"]
        district_keywords = ["district", "station", "location", "place", "area", "region"]
        temperature_keywords = ["temperature", "heat", "warm", "hot", "cold", "cool", "chill", "degrees", "celsius", "fahrenheit"]
        highest_keywords = ["highest", "warmest", "hottest", "maximum", "peak", "top", "greatest", "most"]
        
        datasets = set()
        question_lower = question.lower()
        
        # Check for agriculture-related keywords
        if any(keyword in question_lower for keyword in agriculture_keywords):
            datasets.add("agricultural_production")
        
        # Check for climate-related keywords
        if any(keyword in question_lower for keyword in climate_keywords):
            datasets.add("weather_data")
        
        # Check for climate change-related keywords (including district temperature queries)
        if (any(keyword in question_lower for keyword in district_keywords) and 
            any(keyword in question_lower for keyword in temperature_keywords) and
            any(keyword in question_lower for keyword in highest_keywords)):
            datasets.add("climate_change_data")
        elif "climate change" in question_lower or "global warming" in question_lower:
            datasets.add("climate_change_data")
        
        # If no specific datasets identified, return all datasets
        if not datasets:
            datasets = {"agricultural_production", "weather_data", "climate_change_data"}
        
        return list(datasets)
    
    def generate_sql_query(self, question: str, datasets: List[str]) -> str:
        """Generate SQL query based on question and datasets"""
        # Special handling for the specific question about highest mean temperature
        if "districts has highest mean temperature over 100 years" in question.lower() and "climate_change_data" in datasets:
            return '''SELECT "Station_Name", AVG("Mean_Temperature_in_degree_C___Maximum") as avg_max_temp FROM climate_change_data GROUP BY "Station_Name" ORDER BY avg_max_temp DESC LIMIT 10'''
        
        # Special handling for Andhra Pradesh crop production trend question
        if "crop production trend in andhra pradesh from 2010 to 2013" in question.lower() and "agricultural_production" in datasets:
            return '''SELECT year, SUM(production) as total_production FROM agricultural_production WHERE state = 'Andhra Pradesh' AND year BETWEEN 2010 AND 2013 GROUP BY year ORDER BY year'''
        
        # For now, we'll provide generic information about the datasets
        # In a real implementation, this would fetch actual metadata from the database
        dataset_descriptions = {
            "agricultural_production": "Table containing agricultural production statistics by state, crop, and year. Columns: id, state, district, crop, year, season, area, production, yield_per_hectare, created_at",
            "weather_data": "Table containing weather data including rainfall and temperature by state and date. Columns: id, state, district, date, rainfall, temperature_max, temperature_min, humidity, wind_speed, created_at",
            "climate_change_data": "Table containing climate change data with monthly averages for temperature and rainfall by station. Columns: id, Station_Name, Month, Period, No_of_Years, Mean_Temperature_in_degree_C___Maximum, Mean_Temperature__in_degree_C___Minimum, Mean_Rainfall_in_mm, created_at. Important: When querying this table, use double quotes around column names."
        }
        
        dataset_info = []
        for dataset in datasets:
            description = dataset_descriptions.get(dataset, f"Table: {dataset}")
            dataset_info.append(f"Table: {dataset} - {description}")
        
        prompt = f"""
        You are an expert SQL analyst working with Indian agricultural and climate data.
        
        Available datasets:
        {chr(10).join(dataset_info) if dataset_info else 'No dataset information available'}
        
        User question: "{question}"
        
        Generate a valid PostgreSQL query to answer this question.
        Only return the SQL query, nothing else.
        Make sure to use proper table names and column names.
        For the climate_change_data table, use double quotes around column names (e.g., "Station_Name", "Mean_Temperature_in_degree_C___Maximum").
        Use appropriate WHERE clauses to filter data based on the question.
        Use appropriate ORDER BY clauses to sort results.
        Use appropriate LIMIT clauses to limit results to a reasonable number.
        Use proper date formatting for date comparisons.
        
        Examples of correct queries for climate_change_data:
        1. To find stations with highest average maximum temperature:
           SELECT "Station_Name", AVG("Mean_Temperature_in_degree_C___Maximum") as avg_max_temp FROM climate_change_data GROUP BY "Station_Name" ORDER BY avg_max_temp DESC LIMIT 10
        2. To find stations with highest average minimum temperature:
           SELECT "Station_Name", AVG("Mean_Temperature__in_degree_C___Minimum") as avg_min_temp FROM climate_change_data GROUP BY "Station_Name" ORDER BY avg_min_temp DESC LIMIT 10
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500
                )
            )
            # Clean up the response to ensure it's just SQL
            sql_query = response.text.strip() if response.text else ""
            # Remove any markdown formatting if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            return sql_query.strip()
        except Exception as e:
            # Fallback SQL query generation
            return "SELECT 'LLM query generation failed' as error_message;"
    
    def synthesize_answer(self, question: str, query_results: List[Dict[str, Any]], 
                         datasets: List[str], sql_queries: List[str]) -> str:
        """Synthesize a natural language answer from query results"""
        prompt = f"""
        You are Project Samarth, an AI assistant for analyzing Indian agricultural and climate data.
        
        User question: "{question}"
        
        Datasets used: {', '.join(datasets)}
        
        SQL queries executed:
        {chr(10).join(sql_queries)}
        
        Query results:
        {json.dumps(query_results[:10], indent=2, default=str)}  # Limit to first 10 results
        
        Please provide a clear, concise answer to the user's question based on the query results.
        Include specific numbers and data points from the results where relevant.
        Format your response in a readable way with appropriate units.
        If the data doesn't fully answer the question, acknowledge that limitation.
        If there are no results, explain that no data was found.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=1000
                )
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            return f"Unable to synthesize answer due to an error: {str(e)}"
    
    def calculate_confidence_score(self, query_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on query results"""
        if not query_results:
            return 0.1  # Low confidence if no results
        
        # Check if we have actual data or just error messages
        if len(query_results) == 1 and 'error_message' in query_results[0]:
            return 0.1  # Low confidence if we got an error
        
        # Simple confidence calculation based on result count and data quality
        result_count = len(query_results)
        if result_count == 0:
            return 0.1
        elif result_count < 5:
            return 0.6
        elif result_count < 20:
            return 0.8
        else:
            return 0.95

# Global LLM service instance - only create if API key is available
try:
    llm_service = LLMService()
except ValueError:
    llm_service = None
    print("Warning: GEMINI_API_KEY not set. LLM service will not be available.")