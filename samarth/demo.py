# Demo Script for Project Samarth
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
# The .env file is located in the samarth directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Fallback to default location
    load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from samarth.services.query_service import query_service

async def demo():
    """Demonstrate the capabilities of Project Samarth"""
    print("=== Project Samarth Demo ===")
    print("AI-driven question-answering platform for Indian government datasets")
    print()
    
    # Sample questions to demonstrate functionality
    sample_questions = [
        "What was the crop production trend in Punjab over the last 5 years?",
        "How does monsoon rainfall affect rice production in West Bengal?",
        "Which states had the highest agricultural growth in 2022?",
        "What is the correlation between temperature and wheat yield in Haryana?"
    ]
    
    for i, question in enumerate(sample_questions, 1):
        print(f"Question {i}: {question}")
        print("-" * 50)
        
        try:
            # Process the question through our pipeline
            result = await query_service.process_query(question)
            
            # Display results
            print(f"Answer: {result['answer']}")
            print(f"Data Sources: {', '.join(result['data_sources'])}")
            print(f"Confidence Score: {result['confidence_score']:.2%}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            print("\nSQL Queries Generated:")
            for j, query in enumerate(result['sql_queries'], 1):
                print(f"  {j}. {query}")
            
        except Exception as e:
            print(f"Error processing question: {str(e)}")
        
        print("\n" + "="*60 + "\n")
        
        # Add a small delay between questions
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo())
    
    print("Demo completed! To run the full application:")
    print("1. Set up your actual API keys in the .env file")
    print("2. Run 'uvicorn samarth.main:app --reload' for the API")
    print("3. Run 'streamlit run samarth/frontend/app.py' for the frontend")