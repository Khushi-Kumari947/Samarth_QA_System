# Data Models for Project Samarth
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class AgriculturalProduction(BaseModel):
    """Model for agricultural production data"""
    id: Optional[int] = None
    state: str
    district: Optional[str] = None
    crop: str
    year: int
    season: Optional[str] = None
    area: Optional[float] = None  # in hectares
    production: Optional[float] = None  # in tonnes
    yield_per_hectare: Optional[float] = None  # production/area
    created_at: Optional[datetime] = None

class WeatherData(BaseModel):
    """Model for weather data"""
    id: Optional[int] = None
    state: str
    district: Optional[str] = None
    date: datetime
    rainfall: Optional[float] = None  # in mm
    temperature_max: Optional[float] = None  # in Celsius
    temperature_min: Optional[float] = None  # in Celsius
    humidity: Optional[float] = None  # in percentage
    wind_speed: Optional[float] = None  # in km/h
    created_at: Optional[datetime] = None

class ClimateChangeData(BaseModel):
    """Model for climate change data"""
    id: Optional[int] = None
    station_name: str
    month: str
    period: str
    no_of_years: int
    mean_temperature_max: Optional[float] = None
    mean_temperature_min: Optional[float] = None
    mean_rainfall: Optional[float] = None
    created_at: Optional[datetime] = None

class DatasetMetadata(BaseModel):
    """Model for dataset metadata"""
    id: Optional[int] = None
    dataset_name: str
    resource_id: str
    last_updated: datetime
    record_count: int
    source_url: str
    description: str
    created_at: Optional[datetime] = None

class UserQuery(BaseModel):
    """Model for user queries"""
    id: Optional[int] = None
    question: str
    answer: str
    data_sources: List[str]
    sql_queries: List[str]
    confidence_score: float
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None

class QueryRequest(BaseModel):
    """Model for API query requests"""
    question: str
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    """Model for API query responses"""
    answer: str
    data_sources: List[str]
    sql_queries: List[str]
    visualization_data: Optional[Dict[str, Any]] = None
    confidence_score: float
    execution_time: Optional[float] = None