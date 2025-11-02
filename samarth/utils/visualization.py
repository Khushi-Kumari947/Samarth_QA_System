# Visualization Module for Project Samarth
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from typing import Dict, Any, List, Union
import numpy as np

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
        
        if df.empty:
            return ""
        
        # Clean the data - remove any rows with all NaN values
        df = df.dropna(how='all')
        
        if df.empty:
            return ""
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        # Identify numerical and categorical columns
        numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if chart_type == "bar" and len(df.columns) >= 2:
            # Determine x and y columns
            x_col = df.columns[0]  # First column as x-axis
            y_col = None
            
            # Find the first numerical column for y-axis
            for col in df.columns[1:]:
                if col in numerical_columns:
                    y_col = col
                    break
            
            # If no numerical column found, use the second column if it exists
            if y_col is None and len(df.columns) > 1:
                y_col = df.columns[1]
            
            if y_col is not None:
                # Handle categorical x-axis data
                x_data = df[x_col]
                y_data = df[y_col]
                
                # Convert y_data to numeric if possible
                y_data_numeric = pd.to_numeric(y_data, errors='coerce')
                # Convert to Series to ensure we can call dropna - handle different input types
                if isinstance(y_data_numeric, pd.Series):
                    y_data_clean = y_data_numeric.dropna()
                else:
                    y_data_clean = pd.Series([y_data_numeric]).dropna()
                # Ensure x_data is aligned with cleaned y_data
                if isinstance(x_data, pd.Series):
                    x_data_aligned = x_data.loc[y_data_clean.index]
                else:
                    x_data_series = pd.Series(x_data)
                    x_data_aligned = x_data_series.loc[y_data_clean.index]
                
                if len(x_data_aligned) > 0 and len(y_data_clean) > 0:
                    bars = ax.bar(range(len(x_data_aligned)), y_data_clean, color='#4CAF50')
                    ax.set_xlabel(str(x_col))
                    ax.set_ylabel(str(y_col))
                    
                    # Set x-axis labels
                    if len(x_data_aligned) <= 20:  # Only show labels if not too many
                        ax.set_xticks(range(len(x_data_aligned)))
                        ax.set_xticklabels(x_data_aligned, rotation=45, ha='right')
                    else:
                        # Show every nth label to avoid overcrowding
                        n = len(x_data_aligned) // 10 if len(x_data_aligned) > 10 else 1
                        tick_indices = range(0, len(x_data_aligned), n)
                        ax.set_xticks(tick_indices)
                        ax.set_xticklabels([x_data_aligned.iloc[i] for i in tick_indices], rotation=45, ha='right')
                    
                    # Add value labels on bars if not too many
                    if len(bars) <= 20:
                        for i, (bar, value) in enumerate(zip(bars, y_data_clean)):
                            height = bar.get_height()
                            ax.annotate(f'{value:.1f}' if isinstance(value, float) else str(value),
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),
                                        textcoords="offset points",
                                        ha='center', va='bottom',
                                        fontsize=8)
        
        elif chart_type == "line" and len(df.columns) >= 2:
            # Determine x and y columns
            x_col = df.columns[0]  # First column as x-axis
            y_col = None
            
            # Find the first numerical column for y-axis
            for col in df.columns[1:]:
                if col in numerical_columns:
                    y_col = col
                    break
            
            # If no numerical column found, use the second column if it exists
            if y_col is None and len(df.columns) > 1:
                y_col = df.columns[1]
            
            if y_col is not None:
                # Handle time series or sequential data
                x_data = df[x_col]
                y_data = df[y_col]
                
                # Convert y_data to numeric if possible
                y_data_numeric = pd.to_numeric(y_data, errors='coerce')
                # Ensure we work with Series objects to avoid type issues
                if not isinstance(y_data_numeric, pd.Series):
                    y_data_series = pd.Series(y_data_numeric) if hasattr(y_data_numeric, '__iter__') and not isinstance(y_data_numeric, (str, bytes)) else pd.Series([y_data_numeric])
                else:
                    y_data_series = y_data_numeric
                y_data_clean = y_data_series.dropna()
                x_data_aligned = x_data.loc[y_data_clean.index] if isinstance(x_data, pd.Series) else pd.Series(x_data).loc[y_data_clean.index]  # Match x_data to valid y_data indices
                
                if len(x_data_aligned) > 0 and len(y_data_clean) > 0:
                    ax.plot(range(len(x_data_aligned)), y_data_clean, marker='o', linewidth=2, markersize=6, color='#4CAF50')
                    ax.set_xlabel(str(x_col))
                    ax.set_ylabel(str(y_col))
                    ax.grid(True, alpha=0.3)
                    
                    # Set x-axis labels
                    if len(x_data_aligned) <= 20:  # Only show labels if not too many
                        ax.set_xticks(range(len(x_data_aligned)))
                        ax.set_xticklabels(x_data_aligned, rotation=45, ha='right')
                    else:
                        # Show every nth label to avoid overcrowding
                        n = len(x_data_aligned) // 10 if len(x_data_aligned) > 10 else 1
                        tick_indices = range(0, len(x_data_aligned), n)
                        ax.set_xticks(tick_indices)
                        ax.set_xticklabels([x_data_aligned.iloc[i] for i in tick_indices], rotation=45, ha='right')
        
        elif chart_type == "pie" and len(df.columns) >= 2:
            # Determine label and value columns
            label_col = df.columns[0]  # First column as labels
            value_col = None
            
            # Find the first numerical column for values
            for col in df.columns[1:]:
                if col in numerical_columns:
                    value_col = col
                    break
            
            # If no numerical column found, use the second column if it exists
            if value_col is None and len(df.columns) > 1:
                value_col = df.columns[1]
            
            if value_col is not None:
                # Handle pie chart data
                labels = df[label_col].astype(str)
                values = df[value_col]
                
                # Convert values to numeric if possible
                values_numeric = pd.to_numeric(values, errors='coerce')
                # Convert to Series to ensure we can call dropna - handle different input types
                if isinstance(values_numeric, pd.Series):
                    values_clean = values_numeric.dropna()
                else:
                    values_clean = pd.Series([values_numeric]).dropna()
                # Ensure labels are aligned with cleaned values
                if isinstance(labels, pd.Series):
                    labels_aligned = labels.loc[values_clean.index]
                else:
                    labels_series = pd.Series(labels)
                    labels_aligned = labels_series.loc[values_clean.index]
                
                if len(labels_aligned) > 0 and len(values_clean) > 0:
                    # Take top 10 items for better visualization
                    if len(values_clean) > 10:
                        # Sort by values and take top 10
                        sorted_indices = values_clean.argsort()[::-1][:10]
                        labels_aligned = labels_aligned.iloc[sorted_indices]
                        values_clean = values_clean.iloc[sorted_indices]
                        # Add "Others" category for remaining
                        others_sum = values_clean.iloc[10:].sum()
                        if others_sum > 0:
                            labels_aligned = pd.concat([labels_aligned, pd.Series(["Others"])])
                            values_clean = pd.concat([values_clean, pd.Series([others_sum])])
                    
                    # Create pie chart
                    pie_result = ax.pie(
                        values_clean, 
                        labels=list(labels_aligned.astype(str)), 
                        autopct='%1.1f%%',
                        startangle=90
                    )
                    
                    # Handle variable return types from ax.pie()
                    wedges = pie_result[0]
                    texts = pie_result[1]
                    autotexts = pie_result[2] if len(pie_result) > 2 else []
                    
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                    
                    # Improve text visibility
                    if autotexts:  # Only process autotexts if they exist
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                            autotext.set_fontsize(8)
                    
                    for text in texts:
                        text.set_fontsize(9)
        
        else:
            # Default to simple bar chart with first numerical column
            if numerical_columns:
                col_to_plot = numerical_columns[0]
                if len(df) <= 20:  # Only plot if not too many rows
                    bars = ax.bar(range(len(df)), df[col_to_plot], color='#4CAF50')
                    ax.set_xlabel('Index')
                    ax.set_ylabel(str(col_to_plot))
                    
                    # Add value labels on bars if not too many
                    if len(bars) <= 20:
                        for bar, value in zip(bars, df[col_to_plot]):
                            height = bar.get_height()
                            ax.annotate(f'{value:.1f}' if isinstance(value, float) else str(value),
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),
                                        textcoords="offset points",
                                        ha='center', va='bottom',
                                        fontsize=8)
            elif len(df.columns) > 0:
                # If no numerical columns, try to plot the first column as categorical
                col_to_plot = df.columns[0]
                value_counts = df[col_to_plot].value_counts()
                if len(value_counts) <= 20:  # Only plot if not too many categories
                    bars = ax.bar(range(len(value_counts)), value_counts.values.tolist(), color='#4CAF50')
                    ax.set_xlabel(str(col_to_plot))
                    ax.set_ylabel('Count')
                    ax.set_xticks(range(len(value_counts)))
                    ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
                    
                    # Add value labels on bars
                    for bar, value in zip(bars, value_counts.values.tolist()):
                        height = bar.get_height()
                        ax.annotate(str(value),
                                    xy=(bar.get_x() + bar.get_width() / 2, height),
                                    xytext=(0, 3),
                                    textcoords="offset points",
                                    ha='center', va='bottom',
                                    fontsize=8)
        
        plt.tight_layout()
        
        # Save to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""