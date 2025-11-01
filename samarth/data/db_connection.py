# Database Connection Module
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any, Optional

class DatabaseConnection:
    def __init__(self):
        # Use connection string from .env file
        self.connection_string = os.getenv('DATABASE_URL')
    
    def get_connection(self):
        """Create and return a database connection using connection string"""
        try:
            if self.connection_string:
                conn = psycopg2.connect(
                    self.connection_string,
                    cursor_factory=RealDictCursor
                )
            else:
                # Fallback to individual parameters
                conn = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', '5432'),
                    database=os.getenv('DB_NAME', 'samarth'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', 'password'),
                    cursor_factory=RealDictCursor
                )
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Convert RealDictRow objects to regular dicts
                return [dict(row) for row in results]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE query"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error executing update: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# Global database instance
db = DatabaseConnection()