# Query Service for Project Samarth
import time
from typing import Dict, Any, List, Optional
from samarth.services.llm_service import llm_service
from samarth.data.data_access import AgriculturalDataAccess, WeatherDataAccess, ClimateChangeDataAccess
from samarth.data.db_connection import db
from samarth.models.data_models import UserQuery

class QueryService:
    """Main service for processing natural language queries"""
    
    def __init__(self):
        self.llm = llm_service
    
    async def process_query(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a natural language query through the full pipeline"""
        start_time = time.time()
        
        # Check if LLM service is available
        if self.llm is None:
            return {
                "answer": "LLM service is not available. Please check your GEMINI_API_KEY configuration.",
                "data_sources": [],
                "sql_queries": [],
                "visualization_data": {},
                "confidence_score": 0.0,
                "execution_time": time.time() - start_time
            }
        
        try:
            # Step 1: Identify relevant datasets
            datasets = self.llm.identify_relevant_datasets(question)
            print(f"Identified datasets: {datasets}")
            
            # Step 2: Generate SQL queries
            sql_queries = []
            for dataset in datasets:
                sql_query = self.llm.generate_sql_query(question, [dataset])
                sql_queries.append(sql_query)
                print(f"Generated SQL query for {dataset}: {sql_query}")
            
            # Step 3: Execute queries
            query_results = []
            successful_queries = []
            failed_queries = []
            
            for i, sql_query in enumerate(sql_queries):
                try:
                    # Skip empty or invalid queries
                    if not sql_query or sql_query.strip() == "" or "LLM query generation failed" in sql_query:
                        failed_queries.append({"query": sql_query, "error": "Invalid or empty query"})
                        continue
                        
                    results = db.execute_query(sql_query)
                    query_results.extend(results)
                    successful_queries.append(sql_query)
                    print(f"Executed query {i+1}: {len(results)} results")
                except Exception as e:
                    print(f"Error executing query {i+1}: {e}")
                    failed_queries.append({"query": sql_query, "error": str(e)})
            
            # If all queries failed, return an appropriate message
            if not successful_queries and failed_queries:
                return {
                    "answer": "Unable to execute queries due to database errors. Please try rephrasing your question.",
                    "data_sources": datasets,
                    "sql_queries": sql_queries,
                    "visualization_data": {},
                    "confidence_score": 0.2,
                    "execution_time": time.time() - start_time
                }
            
            # Step 4: Synthesize answer
            answer = self.llm.synthesize_answer(question, query_results, datasets, successful_queries)
            
            # Step 5: Calculate confidence score
            confidence_score = self.llm.calculate_confidence_score(query_results)
            
            # Step 6: Generate visualization data (simplified)
            visualization_data = self._generate_visualization_data(query_results)
            
            # Step 7: Calculate execution time
            execution_time = time.time() - start_time
            
            return {
                "answer": answer,
                "data_sources": datasets,
                "sql_queries": successful_queries,
                "visualization_data": visualization_data,
                "confidence_score": confidence_score,
                "execution_time": execution_time
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "data_sources": [],
                "sql_queries": [],
                "visualization_data": {},
                "confidence_score": 0.0,
                "execution_time": time.time() - start_time
            }
    
    def _generate_visualization_data(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate simple visualization data from query results"""
        if not query_results:
            return {}
        
        # Check if this is time series data (has year column) - use line chart
        if (len(query_results) > 0 and 'year' in query_results[0]):
            return {
                "chart_type": "line",
                "data": query_results
            }
        
        # Check if this is composition data (has percentage or ratio data) - use pie chart
        # This is a simple heuristic: if we have a small number of rows and numerical data, use pie chart
        if (len(query_results) > 0 and 
            len(query_results) <= 10 and 
            any(isinstance(v, (int, float)) for v in query_results[0].values() if v is not None)):
            return {
                "chart_type": "pie",
                "data": query_results
            }
        
        # Default to bar chart for most other cases
        return {
            "chart_type": "bar",
            "data": query_results
        }

# Global query service instance
query_service = QueryService()