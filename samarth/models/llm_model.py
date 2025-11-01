# LLM Model Interface
import os
from openai import AsyncOpenAI
from typing import Optional

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_llm_response(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Get response from LLM based on the provided prompt
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are Project Samarth, an AI assistant for analyzing Indian agricultural and climate data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        return content.strip() if content else "No response generated"
    except Exception as e:
        # Fallback response for development
        return f"LLM response would be generated here. Error: {str(e)}"