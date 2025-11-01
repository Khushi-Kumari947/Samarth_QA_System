# Data Access Layer for Project Samarth
from typing import List, Optional, Dict, Any
from .db_connection import db
from ..models.data_models import AgriculturalProduction, WeatherData, ClimateChangeData, DatasetMetadata, UserQuery

class AgriculturalDataAccess:
    """Data access for agricultural production data"""
    
    @staticmethod
    def get_production_by_state(state: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get agricultural production data for a specific state"""
        query = """
            SELECT * FROM agricultural_production 
            WHERE state = %s 
            ORDER BY year DESC 
            LIMIT %s
        """
        return db.execute_query(query, (state, str(limit)))
    
    @staticmethod
    def get_production_trends(crop: str, state: str) -> List[Dict[str, Any]]:
        """Get production trends for a specific crop in a state"""
        query = """
            SELECT year, production, area, yield_per_hectare
            FROM agricultural_production 
            WHERE crop = %s AND state = %s
            ORDER BY year
        """
        return db.execute_query(query, (crop, state))
    
    @staticmethod
    def get_top_crops_by_production(state: str, year: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top crops by production for a state in a specific year"""
        query = """
            SELECT crop, production, area, yield_per_hectare
            FROM agricultural_production 
            WHERE state = %s AND year = %s
            ORDER BY production DESC
            LIMIT %s
        """
        return db.execute_query(query, (state, year, str(limit)))

    @staticmethod
    def get_production_by_state_and_year_range(state: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Get agricultural production data for a specific state within a year range"""
        query = """
            SELECT year, SUM(production) as total_production
            FROM agricultural_production 
            WHERE state = %s AND year BETWEEN %s AND %s
            GROUP BY year
            ORDER BY year
        """
        return db.execute_query(query, (state, start_year, end_year))

class WeatherDataAccess:
    """Data access for weather data"""
    
    @staticmethod
    def get_weather_by_location(state: str, district: Optional[str] = None, 
                               start_date: Optional[str] = None, 
                               end_date: Optional[str] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get weather data for a location and date range"""
        query = "SELECT * FROM weather_data WHERE state = %s"
        params = [state]
        
        if district:
            query += " AND district = %s"
            params.append(district)
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " ORDER BY date DESC LIMIT %s"
        params.append(str(limit))
        
        return db.execute_query(query, tuple(params))
    
    @staticmethod
    def get_rainfall_stats(state: str, year: int) -> List[Dict[str, Any]]:
        """Get rainfall statistics for a state in a specific year"""
        query = """
            SELECT 
                EXTRACT(MONTH FROM date) as month,
                AVG(rainfall) as avg_rainfall,
                MAX(rainfall) as max_rainfall,
                MIN(rainfall) as min_rainfall
            FROM weather_data 
            WHERE state = %s AND EXTRACT(YEAR FROM date) = %s
            GROUP BY EXTRACT(MONTH FROM date)
            ORDER BY month
        """
        return db.execute_query(query, (state, year))

class ClimateChangeDataAccess:
    """Data access for climate change data"""
    
    @staticmethod
    def get_climate_data_by_station(station_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get climate change data for a specific station"""
        query = """
            SELECT * FROM climate_change_data 
            WHERE Station_Name = %s 
            ORDER BY id 
            LIMIT %s
        """
        return db.execute_query(query, (station_name, str(limit)))
    
    @staticmethod
    def get_climate_data_by_period(period: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get climate change data for a specific period"""
        query = """
            SELECT * FROM climate_change_data 
            WHERE Period = %s 
            ORDER BY Station_Name, Month
            LIMIT %s
        """
        return db.execute_query(query, (period, str(limit)))
    
    @staticmethod
    def get_temperature_trends(station_name: str) -> List[Dict[str, Any]]:
        """Get temperature trends for a specific station"""
        query = """
            SELECT 
                Month,
                Mean_Temperature_in_degree_C___Maximum as max_temp,
                Mean_Temperature__in_degree_C___Minimum as min_temp
            FROM climate_change_data 
            WHERE Station_Name = %s
            ORDER BY 
                CASE Month
                    WHEN 'January' THEN 1
                    WHEN 'February' THEN 2
                    WHEN 'March' THEN 3
                    WHEN 'April' THEN 4
                    WHEN 'May' THEN 5
                    WHEN 'June' THEN 6
                    WHEN 'July' THEN 7
                    WHEN 'August' THEN 8
                    WHEN 'September' THEN 9
                    WHEN 'October' THEN 10
                    WHEN 'November' THEN 11
                    WHEN 'December' THEN 12
                END
        """
        return db.execute_query(query, (station_name,))

class MetadataAccess:
    """Data access for dataset metadata"""
    
    @staticmethod
    def get_dataset_info(dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific dataset"""
        query = "SELECT * FROM dataset_metadata WHERE dataset_name = %s"
        results = db.execute_query(query, (dataset_name,))
        return results[0] if results else None
    
    @staticmethod
    def list_all_datasets() -> List[Dict[str, Any]]:
        """List all available datasets"""
        query = "SELECT dataset_name, description, last_updated FROM dataset_metadata ORDER BY dataset_name"
        return db.execute_query(query)

class UserQueryAccess:
    """Data access for user queries"""
    
    @staticmethod
    def save_query(query: UserQuery) -> bool:
        """Save a user query to the database"""
        insert_query = """
            INSERT INTO user_queries 
            (question, answer, data_sources, sql_queries, confidence_score, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            query.question,
            query.answer,
            query.data_sources,
            query.sql_queries,
            query.confidence_score,
            query.user_id
        )
        return db.execute_update(insert_query, params)
    
    @staticmethod
    def get_recent_queries(limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent user queries"""
        query = "SELECT * FROM user_queries ORDER BY created_at DESC LIMIT %s"
        return db.execute_query(query, (str(limit),))