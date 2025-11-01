# Visualization Module for Project Samarth
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from typing import Dict, Any, List

def create_visualization(data: List[Dict[Any, Any]], chart_type: str = "bar") -> str:
    """
    Create a visualization from data and return as base64 encoded image
    
    Args:
        data: List of dictionaries containing data points
        chart_type: Type of chart to generate (bar, line, pie)
        
    Returns:
        str: Base64 encoded image string
    """
    if not data:
        return ""
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == "bar" and len(df.columns) >= 2:
            # Bar chart with first column as x-axis and second as y-axis
            ax.bar(df.iloc[:, 0], df.iloc[:, 1])
            ax.set_xlabel(str(df.columns[0]))
            ax.set_ylabel(str(df.columns[1]))
            ax.tick_params(axis='x', rotation=45)
            
        elif chart_type == "line" and len(df.columns) >= 2:
            # Line chart
            ax.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o')
            ax.set_xlabel(str(df.columns[0]))
            ax.set_ylabel(str(df.columns[1]))
            ax.tick_params(axis='x', rotation=45)
            
        elif chart_type == "pie" and len(df.columns) >= 2:
            # Pie chart (first column as labels, second as values)
            ax.pie(df.iloc[:, 1], labels=df.iloc[:, 0], autopct='%1.1f%%')
            ax.axis('equal')
            
        else:
            # Default to simple bar chart
            if len(df.columns) >= 1:
                df.iloc[:, 0].value_counts().plot(kind='bar', ax=ax)
                ax.set_xlabel(str(df.columns[0]))
                ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        return ""