# ETL Pipeline for Government Datasets
import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables when running standalone
if __name__ == "__main__":
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()

# Handle imports for both module and standalone execution
try:
    # When running as part of the samarth module
    from samarth.data.db_connection import db
except ImportError:
    try:
        # When running standalone, import directly from data directory
        from data.db_connection import db
    except ImportError:
        # Fallback to direct import
        try:
            from db_connection import db
        except ImportError:
            # If all else fails, create a mock database connection
            print("Warning: Could not import database connection module")
            db = None

class ETLPipeline:
    """ETL Pipeline for integrating government datasets from data.gov.in"""
    
    def __init__(self):
        self.api_key = os.getenv("DATA_GOV_IN_API_KEY")
        self.base_url = "https://api.data.gov.in/resource/"
        
    def fetch_agriculture_data_filtered(self, resource_id: str, start_state: str = "", min_year: int = 2010, crop_filter: str = "Total-Pulse", limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch agricultural data from Ministry of Agriculture & Farmers Welfare, 
        optionally starting from a specific state, with filtering by year and crop type"""
        try:
            url = f"{self.base_url}{resource_id}"
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": limit
            }
            
            print(f"Fetching agricultural data from: {url}")
            if self.api_key:
                print(f"API Key: {self.api_key[:10]}...")  # Print first 10 characters of API key for debugging
            else:
                print("API Key: None")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Print the raw API response structure for debugging
            print("Raw API response structure:")
            if "records" in data:
                records = data["records"]
                print(f"Number of records: {len(records)}")
                if records:
                    print("First record keys:", list(records[0].keys()) if records else "No records")
                    print("First record:", records[0] if records else "No records")
            else:
                print("Response keys:", list(data.keys()))
                print("Full response:", data)
            
            records = data.get("records", [])
            
            print(f"Fetched {len(records)} agricultural records")
            
            # Transform data to match our schema
            transformed_records = []
            
            # Process all records and extract crop data
            start_processing = start_state == ""  # If no start_state, start processing immediately
            
            for i, record in enumerate(records):
                state = record.get("state_ut_name")
                if not state:
                    continue
                    
                # If we have a start_state, begin processing when we reach it
                if not start_processing:
                    if state == start_state:
                        start_processing = True
                    else:
                        continue  # Skip until we reach the start_state
                        
                # Process each field in the record to extract crop data
                for field_name, production_str in record.items():
                    if production_str not in [None, "NA", ""] and field_name != "state_ut_name":
                        # Try to parse the field name to extract crop and year
                        try:
                            # Handle different field name patterns
                            crop_name = "Unknown"
                            year = 2015  # Default year
                            
                            # Pattern 1: food_grains_cereals__rice__production_is_thausand_toones__2009_10
                            if "__" in field_name and "production" in field_name:
                                parts = field_name.split("__")
                                if len(parts) >= 2:
                                    crop_name = parts[1].split("__")[0].title()
                                    # Extract year from the end
                                    if "__" in field_name and field_name.count("__") >= 3:
                                        year_part = field_name.split("__")[-1]
                                        if year_part.startswith("20"):
                                            year_str = year_part.split("_")[0]
                                            year = int(year_str)
                            
                            # Pattern 2: rice_2013_14
                            elif "_" in field_name and field_name.count("_") >= 2:
                                parts = field_name.split("_")
                                if parts[-1].isdigit() and parts[-2].isdigit():
                                    crop_name = "_".join(parts[:-2]).title()
                                    year = int(parts[-2])
                            
                            # Pattern 3: rice__th_tonnes__2014_15
                            elif field_name.count("__") >= 2:
                                parts = field_name.split("__")
                                if len(parts) >= 3 and parts[-1].startswith("20"):
                                    year_part = parts[-1]
                                    year_parts = year_part.split("_")
                                    if len(year_parts) >= 2:
                                        year = int(year_parts[0])
                                    crop_name = parts[0].title()
                            
                            # Filter out invalid crop names (as per requirements)
                            invalid_crops = ["production_is_thousand", "production_is_thausand", "production_is_thausand_toones"]
                            if any(invalid_crop in crop_name.lower() for invalid_crop in invalid_crops):
                                continue  # Skip this record
                            
                            # Apply filters
                            # Filter by year (only include records after min_year)
                            if year < min_year:
                                continue
                                
                            # Filter by crop type if specified
                            if crop_filter and crop_filter.lower() not in crop_name.lower():
                                continue
                            
                            # Convert production to float
                            production = float(production_str)
                            
                            transformed_record = {
                                "state": state,
                                "district": "State Level",  # This is state-level data
                                "crop": crop_name,
                                "year": year,
                                "season": "Annual",  # Default value
                                "area": 0.0,  # Not available in this dataset
                                "production": production,
                                "yield_per_hectare": 0.0  # Not available in this dataset
                            }
                            
                            # Print first few records for debugging
                            if i < 1 and len(transformed_records) < 5:
                                print(f"Transformed record {len(transformed_records)}: {transformed_record}")
                            
                            transformed_records.append(transformed_record)
                        except (ValueError, IndexError):
                            # Skip if we can't parse the field name or convert to float
                            continue
            
            return transformed_records
        except Exception as e:
            print(f"Error fetching agriculture data: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_weather_data_filtered(self, resource_id: str, states = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch weather data from India Meteorological Department (IMD), optionally filtering by states"""
        try:
            url = f"{self.base_url}{resource_id}"
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": limit
            }
            
            print(f"Fetching weather data from: {url}")
            if self.api_key:
                print(f"API Key: {self.api_key[:10]}...")  # Print first 10 characters of API key for debugging
            else:
                print("API Key: None")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Print the raw API response structure for debugging
            print("Raw API response structure:")
            if "records" in data:
                records = data["records"]
                print(f"Number of records: {len(records)}")
                if records:
                    print("First record keys:", list(records[0].keys()) if records else "No records")
                    print("First record:", records[0] if records else "No records")
            else:
                print("Response keys:", list(data.keys()))
                print("Full response:", data)
            
            records = data.get("records", [])
            
            print(f"Fetched {len(records)} weather records")
            
            # Transform data to match our schema
            transformed_records = []
            month_mapping = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
            }
            
            for i, record in enumerate(records):
                # Updated to match actual API response structure from the log
                state_ut = record.get("state_ut")
                district = record.get("district")
                
                # Based on the API response you showed, there's no explicit 'year' field
                # The data seems to be organized by state/district with monthly values
                # We'll need to handle this differently
                
                # For now, let's check if there's any metadata in the response that might contain year info
                year = 2020  # Default year
                
                # Skip if essential fields are missing
                if not state_ut:
                    print(f"Skipping record {i} due to missing state_ut")
                    continue
                
                # If we have a state filter, only process records for those states
                if states is not None and state_ut not in states:
                    print(f"Skipping record {i} due to state filter: {state_ut} not in {states}")
                    continue
                
                # Use state_ut as state since that's what the API provides
                state = state_ut
                
                # For each month column, create a separate record with approximate dates
                for month_abbr, month_num in month_mapping.items():
                    if month_abbr in record:
                        rainfall_str = record.get(month_abbr)
                        rainfall = 0.0
                        if rainfall_str not in [None, "NA", "", "NULL"]:
                            try:
                                rainfall = float(rainfall_str)
                            except ValueError:
                                print(f"Could not convert rainfall value '{rainfall_str}' to float")
                                pass
                        
                        # Create a date for the middle of the month
                        date_str = f"{year}-{month_num:02d}-15"
                        
                        transformed_record = {
                            "state": state,
                            "district": district if district else "Unknown",
                            "date": date_str,
                            "rainfall": rainfall,
                            "temperature_max": 0.0,  # Not available in this dataset
                            "temperature_min": 0.0,  # Not available in this dataset
                            "humidity": 0.0,  # Not available in this dataset
                            "wind_speed": 0.0  # Not available in this dataset
                        }
                        
                        # Print first few records for debugging
                        if len(transformed_records) < 5:
                            print(f"Transformed record {len(transformed_records)}: {transformed_record}")
                        
                        transformed_records.append(transformed_record)
            
            print(f"Transformed {len(transformed_records)} weather records")
            return transformed_records
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_weather_data(self, resource_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch weather data from India Meteorological Department (IMD)"""
        try:
            url = f"{self.base_url}{resource_id}"
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": limit
            }
            
            print(f"Fetching weather data from: {url}")
            if self.api_key:
                print(f"API Key: {self.api_key[:10]}...")  # Print first 10 characters of API key for debugging
            else:
                print("API Key: None")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Print the raw API response structure for debugging
            print("Raw API response structure:")
            if "records" in data:
                records = data["records"]
                print(f"Number of records: {len(records)}")
                if records:
                    print("First record keys:", list(records[0].keys()) if records else "No records")
                    print("First record:", records[0] if records else "No records")
            else:
                print("Response keys:", list(data.keys()))
                print("Full response:", data)
            
            records = data.get("records", [])
            
            print(f"Fetched {len(records)} weather records")
            
            # Transform data to match our schema
            transformed_records = []
            month_mapping = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
            }
            
            for i, record in enumerate(records):
                # Updated to match actual API response structure
                subdivision = record.get("subdivision")
                year = record.get("year")
                
                # Skip if essential fields are missing
                if not subdivision or not year:
                    continue
                
                # Split subdivision to get state/district if possible
                # For now, we'll use subdivision as state and "Unknown" as district
                state = subdivision
                district = "Unknown"
                
                # For each month column, create a separate record with approximate dates
                for month_abbr, month_num in month_mapping.items():
                    if month_abbr in record:
                        rainfall_str = record.get(month_abbr)
                        rainfall = 0.0
                        if rainfall_str not in [None, "NA", "", "NULL"]:
                            try:
                                rainfall = float(rainfall_str)
                            except ValueError:
                                pass
                        
                        # Create a date for the middle of the month
                        try:
                            year_int = int(year)
                            date_str = f"{year_int}-{month_num:02d}-15"
                        except ValueError:
                            # Use default year if parsing fails
                            date_str = f"2000-{month_num:02d}-15"
                        
                        transformed_record = {
                            "state": state,
                            "district": district,
                            "date": date_str,
                            "rainfall": rainfall,
                            "temperature_max": 0.0,  # Not available in this dataset
                            "temperature_min": 0.0,  # Not available in this dataset
                            "humidity": 0.0,  # Not available in this dataset
                            "wind_speed": 0.0  # Not available in this dataset
                        }
                        
                        # Print first few records for debugging
                        if i < 1 and len(transformed_records) < 5:
                            print(f"Transformed record {len(transformed_records)}: {transformed_record}")
                        
                        transformed_records.append(transformed_record)
            
            return transformed_records
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_agriculture_data(self, resource_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch agricultural data from Ministry of Agriculture & Farmers Welfare"""
        try:
            url = f"{self.base_url}{resource_id}"
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": limit
            }
            
            print(f"Fetching agricultural data from: {url}")
            if self.api_key:
                print(f"API Key: {self.api_key[:10]}...")  # Print first 10 characters of API key for debugging
            else:
                print("API Key: None")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Print the raw API response structure for debugging
            print("Raw API response structure:")
            if "records" in data:
                records = data["records"]
                print(f"Number of records: {len(records)}")
                if records:
                    print("First record keys:", list(records[0].keys()) if records else "No records")
                    print("First record:", records[0] if records else "No records")
            else:
                print("Response keys:", list(data.keys()))
                print("Full response:", data)
            
            records = data.get("records", [])
            
            print(f"Fetched {len(records)} agricultural records")
            
            # Transform data to match our schema
            transformed_records = []
            
            # Process all records and extract crop data
            for i, record in enumerate(records):
                state = record.get("state_ut_name")
                if not state:
                    continue
                    
                # Process each field in the record to extract crop data
                for field_name, production_str in record.items():
                    if production_str not in [None, "NA", ""] and field_name != "state_ut_name":
                        # Try to parse the field name to extract crop and year
                        try:
                            # Handle different field name patterns
                            crop_name = "Unknown"
                            year = 2015  # Default year
                            
                            # Pattern 1: food_grains_cereals__rice__production_is_thausand_toones__2009_10
                            if "__" in field_name and "production" in field_name:
                                parts = field_name.split("__")
                                if len(parts) >= 2:
                                    crop_name = parts[1].split("__")[0].title()
                                    # Extract year from the end
                                    if "__" in field_name and field_name.count("__") >= 3:
                                        year_part = field_name.split("__")[-1]
                                        if year_part.startswith("20"):
                                            year_str = year_part.split("_")[0]
                                            year = int(year_str)
                            
                            # Pattern 2: rice_2013_14
                            elif "_" in field_name and field_name.count("_") >= 2:
                                parts = field_name.split("_")
                                if parts[-1].isdigit() and parts[-2].isdigit():
                                    crop_name = "_".join(parts[:-2]).title()
                                    year = int(parts[-2])
                            
                            # Pattern 3: rice__th_tonnes__2014_15
                            elif field_name.count("__") >= 2:
                                parts = field_name.split("__")
                                if len(parts) >= 3 and parts[-1].startswith("20"):
                                    year_part = parts[-1]
                                    year_parts = year_part.split("_")
                                    if len(year_parts) >= 2:
                                        year = int(year_parts[0])
                                    crop_name = parts[0].title()
                            
                            # Filter out invalid crop names (as per requirements)
                            invalid_crops = ["production_is_thousand", "production_is_thausand", "production_is_thausand_toones"]
                            if any(invalid_crop in crop_name.lower() for invalid_crop in invalid_crops):
                                continue  # Skip this record
                            
                            # Filter by year (only include records from 2010 onwards)
                            if year < 2010:
                                continue
                            
                            # Convert production to float
                            production = float(production_str)
                            
                            transformed_record = {
                                "state": state,
                                "district": "State Level",  # This is state-level data
                                "crop": crop_name,
                                "year": year,
                                "season": "Annual",  # Default value
                                "area": 0.0,  # Not available in this dataset
                                "production": production,
                                "yield_per_hectare": 0.0  # Not available in this dataset
                            }
                            
                            # Print first few records for debugging
                            if i < 1 and len(transformed_records) < 5:
                                print(f"Transformed record {len(transformed_records)}: {transformed_record}")
                            
                            transformed_records.append(transformed_record)
                        except (ValueError, IndexError):
                            # Skip if we can't parse the field name or convert to float
                            continue
            
            return transformed_records
        except Exception as e:
            print(f"Error fetching agriculture data: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def store_agricultural_data(self, data: List[Dict[str, Any]]) -> bool:
        """Store agricultural data in the data warehouse"""
        try:
            if db is None:
                print("Database connection not available")
                return False
                
            # Use the execute_update method for consistency
            insert_query = """
                INSERT INTO agricultural_production 
                (state, district, crop, year, season, production)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            success_count = 0
            for i, record in enumerate(data):
                params = (
                    record.get("state"),
                    record.get("district"),
                    record.get("crop"),
                    record.get("year"),
                    record.get("season"),
                    record.get("production")
                )
                
                # Print first few records for debugging
                if i < 3:
                    print(f"Inserting agricultural record {i}: {params}")
                
                if db.execute_update(insert_query, params):
                    success_count += 1
            
            print(f"Successfully stored {success_count} agricultural records")
            return success_count == len(data)
        except Exception as e:
            print(f"Error storing agricultural data: {str(e)}")
            return False
    
    def store_weather_data(self, data: List[Dict[str, Any]]) -> bool:
        """Store weather data in the data warehouse"""
        try:
            if db is None:
                print("Database connection not available")
                return False
                
            # Use the execute_update method for consistency
            insert_query = """
                INSERT INTO weather_data 
                (state, district, date, rainfall, temperature_max, temperature_min, humidity, wind_speed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            success_count = 0
            for i, record in enumerate(data):
                params = (
                    record.get("state"),
                    record.get("district"),
                    record.get("date"),
                    record.get("rainfall"),
                    record.get("temperature_max"),
                    record.get("temperature_min"),
                    record.get("humidity"),
                    record.get("wind_speed")
                )
                
                # Print first few records for debugging
                if i < 3:
                    print(f"Inserting weather record {i}: {params}")
                
                if db.execute_update(insert_query, params):
                    success_count += 1
            
            print(f"Successfully stored {success_count} weather records")
            return success_count == len(data)
        except Exception as e:
            print(f"Error storing weather data: {str(e)}")
            return False
    
    def store_climate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Store climate change data in the data warehouse"""
        try:
            if db is None:
                print("Database connection not available")
                return False
                
            # Use the execute_update method for consistency
            insert_query = """
                INSERT INTO climate_change_data 
                (Station_Name, Month, Period, No_of_Years, Mean_Temperature_in_degree_C___Maximum, 
                 Mean_Temperature__in_degree_C___Minimum, Mean_Rainfall_in_mm)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            success_count = 0
            for i, record in enumerate(data):
                params = (
                    record.get("Station_Name"),
                    record.get("Month"),
                    record.get("Period"),
                    record.get("No_of_Years"),
                    record.get("Mean_Temperature_in_degree_C___Maximum"),
                    record.get("Mean_Temperature__in_degree_C___Minimum"),
                    record.get("Mean_Rainfall_in_mm")
                )
                
                # Print first few records for debugging
                if i < 3:
                    print(f"Inserting climate record {i}: {params}")
                
                if db.execute_update(insert_query, params):
                    success_count += 1
            
            print(f"Successfully stored {success_count} climate records")
            return success_count == len(data)
        except Exception as e:
            print(f"Error storing climate data: {str(e)}")
            return False
    
    def update_metadata(self, dataset_name: str, resource_id: str, record_count: int, description: str) -> bool:
        """Update dataset metadata in the metadata layer"""
        try:
            if db is None:
                print("Database connection not available")
                return False
                
            # Use the execute_update method for consistency
            upsert_query = """
                INSERT INTO dataset_metadata 
                (dataset_name, resource_id, last_updated, record_count, source_url, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (dataset_name) 
                DO UPDATE SET 
                    last_updated = EXCLUDED.last_updated,
                    record_count = EXCLUDED.record_count
            """
            
            params = (
                dataset_name,
                resource_id,
                datetime.now(),
                record_count,
                f"https://api.data.gov.in/resource/{resource_id}",
                description
            )
            
            success = db.execute_update(upsert_query, params)
            if success:
                print(f"Successfully updated metadata for {dataset_name}")
            else:
                print(f"Failed to update metadata for {dataset_name}")
            return success
        except Exception as e:
            print(f"Error updating metadata: {str(e)}")
            return False
    
    def run_agriculture_etl(self, resource_id: str) -> bool:
        """Run complete ETL pipeline for agricultural data"""
        print("Starting agricultural data ETL pipeline...")
        
        # Extract
        data = self.fetch_agriculture_data(resource_id)
        if not data:
            print("No agricultural data fetched")
            return False
        
        # Transform and Load
        success = self.store_agricultural_data(data)
        if success:
            # Update metadata
            self.update_metadata(
                "agricultural_production",
                resource_id,
                len(data),
                "Agricultural production statistics from Ministry of Agriculture & Farmers Welfare"
            )
            print("Agricultural data ETL pipeline completed successfully")
        else:
            print("Failed to store agricultural data")
        
        return success
    
    def run_weather_etl(self, resource_id: str) -> bool:
        """Run complete ETL pipeline for weather data"""
        print("Starting weather data ETL pipeline...")
        
        # Extract
        data = self.fetch_weather_data(resource_id)
        if not data:
            print("No weather data fetched")
            return False
        
        # Transform and Load
        success = self.store_weather_data(data)
        if success:
            # Update metadata
            self.update_metadata(
                "weather_data",
                resource_id,
                len(data),
                "Weather data from India Meteorological Department (IMD)"
            )
            print("Weather data ETL pipeline completed successfully")
        else:
            print("Failed to store weather data")
        
        return success
    
    def run_climate_etl_from_csv(self, csv_file_path: str) -> bool:
        """Run ETL pipeline for climate change data from CSV file"""
        print(f"Starting climate change data ETL pipeline from {csv_file_path}...")
        
        try:
            import pandas as pd
            
            # Extract
            df = pd.read_csv(csv_file_path)
            print(f"Loaded {len(df)} records from {csv_file_path}")
            
            # Transform - Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Load
            success = self.store_climate_data(data)
            if success:
                # Update metadata
                self.update_metadata(
                    "climate_change_data",
                    "csv-import",
                    len(data),
                    "Climate change data imported from CSV file"
                )
                print("Climate change data ETL pipeline completed successfully")
            else:
                print("Failed to store climate change data")
            
            return success
            
        except Exception as e:
            print(f"Error in climate change data ETL pipeline: {str(e)}")
            return False
    
    def run_agriculture_etl_incremental(self, resource_id: str, start_state: str = "", min_year: int = 2010, crop_filter: str = "Total-Pulse") -> bool:
        """Run incremental ETL pipeline for agricultural data, starting from a specific state, 
        with filtering by year and crop type"""
        print(f"Starting incremental agricultural data ETL pipeline from state: {start_state}...")
        print(f"Filtering for year >= {min_year} and crop containing '{crop_filter}'")
        
        # Extract with filtering
        data = self.fetch_agriculture_data_filtered(resource_id, start_state, min_year, crop_filter)
        if not data:
            print("No agricultural data fetched")
            return False
        
        # Transform and Load
        success = self.store_agricultural_data(data)
        if success:
            # Update metadata
            self.update_metadata(
                "agricultural_production",
                resource_id,
                len(data),
                f"Agricultural production statistics from Ministry of Agriculture & Farmers Welfare (incremental from {start_state}, year >= {min_year}, crop filter: {crop_filter})"
            )
            print("Incremental agricultural data ETL pipeline completed successfully")
        else:
            print("Failed to store agricultural data")
        
        return success

    def run_weather_etl_filtered(self, resource_id: str, states = None) -> bool:
        """Run filtered ETL pipeline for weather data, optionally filtering by states"""
        state_info = f" for states: {states}" if states is not None else ""
        print(f"Starting filtered weather data ETL pipeline{state_info}...")
        
        # Extract
        data = self.fetch_weather_data_filtered(resource_id, states)
        if not data:
            print("No weather data fetched")
            return False
        
        # Transform and Load
        success = self.store_weather_data(data)
        if success:
            # Update metadata
            self.update_metadata(
                "weather_data",
                resource_id,
                len(data),
                f"Weather data from India Meteorological Department (IMD){state_info}"
            )
            print("Filtered weather data ETL pipeline completed successfully")
        else:
            print("Failed to store weather data")
        
        return success

def run_complete_etl_pipeline():
    """Run the complete ETL pipeline for all datasets"""
    pipeline = ETLPipeline()
    
    # Resource IDs for datasets (these would be actual IDs from data.gov.in)
    agriculture_resource_id = os.getenv("AGRICULTURE_RESOURCE_ID", "agri-resource-001")
    weather_resource_id = os.getenv("WEATHER_RESOURCE_ID", "weather-resource-001")
    
    print("Starting complete ETL pipeline...")
    print(f"Using AGRICULTURE_RESOURCE_ID: {agriculture_resource_id}")
    print(f"Using WEATHER_RESOURCE_ID: {weather_resource_id}")
    
    # Run agricultural data ETL
    agri_success = pipeline.run_agriculture_etl(agriculture_resource_id)
    
    # Run weather data ETL
    weather_success = pipeline.run_weather_etl(weather_resource_id)
    
    if agri_success and weather_success:
        print("Complete ETL pipeline finished successfully!")
        return True
    else:
        print("Complete ETL pipeline finished with some errors")
        return False

def run_incremental_etl_pipeline():
    """Run the incremental ETL pipeline for remaining agricultural data and weather data"""
    pipeline = ETLPipeline()
    
    # Resource IDs for datasets (these would be actual IDs from data.gov.in)
    agriculture_resource_id = os.getenv("AGRICULTURE_RESOURCE_ID", "agri-resource-001")
    weather_resource_id = os.getenv("WEATHER_RESOURCE_ID", "weather-resource-001")
    
    print("Starting incremental ETL pipeline...")
    print(f"Using AGRICULTURE_RESOURCE_ID: {agriculture_resource_id}")
    print(f"Using WEATHER_RESOURCE_ID: {weather_resource_id}")
    
    # Run incremental agricultural data ETL starting from the state after Odisha (Orissa)
    # States after Odisha in alphabetical order would be: Punjab, Rajasthan, Sikkim, Tamil Nadu, etc.
    # Let's start from Punjab
    agri_success = pipeline.run_agriculture_etl_incremental(
        agriculture_resource_id, 
        start_state="Punjab", 
        min_year=2010, 
        crop_filter=""  # Remove crop filter to get all crops
    )
    
    # Run weather data ETL for all states (or you can specify specific states)
    weather_success = pipeline.run_weather_etl_filtered(weather_resource_id)
    
    if agri_success and weather_success:
        print("Incremental ETL pipeline finished successfully!")
        return True
    else:
        print("Incremental ETL pipeline finished with some errors")
        return False

if __name__ == "__main__":
    # Load environment variables when running standalone
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    run_complete_etl_pipeline()