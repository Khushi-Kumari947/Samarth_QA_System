import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_custom_table(table_name, columns):
    """
    Create a custom table in the database
    columns: list of tuples (column_name, column_type)
    Example: [("name", "TEXT"), ("age", "INTEGER"), ("salary", "DECIMAL")]
    """
    try:
        # Import psycopg2 after ensuring it's available
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Get the database URL from .env
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not found. Make sure it's set in your .env file.")
        
        # Create database connection
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        
        # Create column definitions
        column_definitions = []
        for col_name, col_type in columns:
            column_definitions.append(f'"{col_name}" {col_type}')
        
        # Create table SQL
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            {', '.join(column_definitions)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Execute table creation
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Custom table '{table_name}' created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating custom table: {str(e)}")
        return False

def initialize_database():
    """
    Initialize the database with required tables
    """
    try:
        # Import psycopg2 after ensuring it's available
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Get the database URL from .env
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not found. Make sure it's set in your .env file.")
        
        # Create database connection
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        
        # Create tables for agricultural data
        create_agricultural_table = """
            CREATE TABLE IF NOT EXISTS agricultural_production (
                id SERIAL PRIMARY KEY,
                state VARCHAR(100),
                district VARCHAR(100),
                crop VARCHAR(100),
                year INTEGER,
                season VARCHAR(50),
                area DECIMAL,
                production DECIMAL,
                yield_per_hectare DECIMAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Create tables for weather data
        create_weather_table = """
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                state VARCHAR(100),
                district VARCHAR(100),
                date DATE,
                rainfall DECIMAL,
                temperature_max DECIMAL,
                temperature_min DECIMAL,
                humidity DECIMAL,
                wind_speed DECIMAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Create table for climate change data
        create_climate_table = """
            CREATE TABLE IF NOT EXISTS climate_change_data (
                id SERIAL PRIMARY KEY,
                Station_Name TEXT,
                Month TEXT,
                Period TEXT,
                No_of_Years INTEGER,
                Mean_Temperature_in_degree_C___Maximum NUMERIC,
                Mean_Temperature__in_degree_C___Minimum NUMERIC,
                Mean_Rainfall_in_mm NUMERIC,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Create metadata table for dataset tracking
        create_metadata_table = """
            CREATE TABLE IF NOT EXISTS dataset_metadata (
                id SERIAL PRIMARY KEY,
                dataset_name VARCHAR(100),
                resource_id VARCHAR(100),
                last_updated TIMESTAMP,
                record_count INTEGER,
                source_url TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Create user queries table for logging
        create_queries_table = """
            CREATE TABLE IF NOT EXISTS user_queries (
                id SERIAL PRIMARY KEY,
                question TEXT,
                answer TEXT,
                data_sources TEXT[],
                sql_queries TEXT[],
                confidence_score DECIMAL,
                user_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Execute table creation queries
        cursor = conn.cursor()
        cursor.execute(create_agricultural_table)
        cursor.execute(create_weather_table)
        cursor.execute(create_climate_table)
        cursor.execute(create_metadata_table)
        cursor.execute(create_queries_table)
        
        # Insert sample metadata
        try:
            insert_metadata = """
                INSERT INTO dataset_metadata (dataset_name, resource_id, last_updated, record_count, source_url, description)
                VALUES 
                    ('agricultural_production', 'agri-001', NOW(), 0, 'https://data.gov.in', 'Agricultural production statistics by state and crop'),
                    ('weather_data', 'weather-001', NOW(), 0, 'https://data.gov.in', 'Weather data including rainfall and temperature'),
                    ('climate_change_data', 'climate-001', NOW(), 0, 'https://data.gov.in', 'Climate change data including temperature and rainfall trends')
                ON CONFLICT (dataset_name) DO NOTHING
            """
            cursor.execute(insert_metadata)
        except Exception as e:
            print(f"Note: Could not insert sample metadata (may already exist): {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

if __name__ == "__main__":
    initialize_database()