# Example API Client for Project Samarth
import requests
import json
from typing import Dict, Any, Optional

class SamarthAPIClient:
    def __init__(self, base_url: str = "http://samarthqasystem-production.up.railway.app"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def ask_question(self, question: str, user_id: Optional[str] = None) -> Dict[Any, Any]:
        """
        Ask a question to the Samarth API
        
        Args:
            question (str): The natural language question to ask
            user_id (str, optional): User identifier for tracking
            
        Returns:
            dict: API response containing answer and metadata
        """
        url = f"{self.base_url}/api/v1/query/ask"
        
        payload = {
            "question": question
        }
        
        if user_id:
            payload["user_id"] = user_id
            
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = SamarthAPIClient()
    
    # Example questions
    questions = [
        "What is the trend of rice production in India over the last decade?",
        "How does rainfall affect crop yield in Maharashtra?",
        "Which state had the highest agricultural growth in 2022?"
    ]
    
    print("=== Project Samarth API Client Demo ===\n")
    
    for question in questions:
        print(f"Question: {question}")
        print("-" * 40)
        
        # Ask the question
        result = client.ask_question(question)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Answer: {result['answer']}")
            print(f"Sources: {', '.join(result['data_sources'])}")
            print(f"Confidence: {result['confidence_score']:.2%}")
            
        print("\n" + "="*50 + "\n")