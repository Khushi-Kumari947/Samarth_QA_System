import streamlit as st
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import sys
from typing import List, Dict, Any, Callable

# Add the parent directory to sys.path to enable importing samarth modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import visualization module with error handling
try:
    from samarth.utils.visualization import create_visualization
except ImportError:
    # Fallback implementation
    def create_visualization(data: List[Dict[Any, Any]], chart_type: str = "bar") -> str:
        return ""

# Load environment variables from .env file
# The .env file is located in the samarth directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Fallback to default location
    load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Project Samarth",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Force black background for entire app */
    body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #000000 !important;
        color: #cccccc !important;
    }
    
    /* Main header */
    .main-header {
        font-size: 3.0rem !important;
        font-weight: 700 !important;
        color: #aaaaaa !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.8rem !important;
        font-weight: 500 !important;
        color: #999999 !important;
        margin-bottom: 1rem;
        text-align: center;
    }
    .response-box {
        border: 1px solid #444444;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #ffffff !important;
        color: #000000 !important;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    .error-box {
        border: 1px solid #f44336;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #ffebee !important;
        color: #000000 !important;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    .info-box {
        border: 1px solid #1976D2;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #E3F2FD !important;
        color: #000000 !important;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    .data-source-box {
        border: 1px solid #388E3C;
        border-radius: 10px;
        padding: 1rem;
        background-color: #E8F5E9 !important;
        color: #000000 !important;
        margin-top: 1rem;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    .sql-query-box {
        border: 1px solid #F57C00;
        border-radius: 10px;
        padding: 1rem;
        background-color: #FFF3E0 !important;
        color: #000000 !important;
        font-family: monospace;
        margin-top: 1rem;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    .metric-card {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
        color: #000000 !important;
        border: 1px solid #eeeeee !important;
    }
    .metric-value {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #4CAF50 !important;
    }
    .metric-label {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #000000 !important;
    }
    .visualization-container {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
        margin-top: 1rem;
        color: #000000 !important;
        border: 1px solid #eeeeee !important;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        color: #777777 !important;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    .example-question {
        background-color: #222222 !important; /* Darker background for better visibility */
        border-left: 4px solid #4CAF50; /* Green border for better visibility */
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        border-radius: 0 4px 4px 0;
        box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
        color: #ffffff !important; /* White text for better visibility */
        font-weight: 400 !important;
        font-size: 1.0rem !important;
    }
    .example-question strong {
        color: #4CAF50 !important; /* Green text for better visibility */
        font-weight: 600 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        color: #cccccc !important;
        background-color: #111111 !important;
        font-size: 1.0rem !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #cccccc !important;
        font-weight: 400 !important;
    }
    
    section[data-testid="stSidebar"] h1 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #4CAF50 !important; /* Green color for better visibility */
    }
    
    section[data-testid="stSidebar"] h2 {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        color: #81C784 !important; /* Light green for better visibility */
    }
    
    section[data-testid="stSidebar"] h3 {
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        color: #81C784 !important; /* Light green for better visibility */
    }
    
    /* Text inputs */
    textarea[kind="text-input"], input[kind="text-input"] {
        color: #cccccc !important;
        background-color: #222222 !important;
        border: 1px solid #333333 !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    
    /* Buttons */
    button[kind="secondary"] {
        color: #cccccc !important;
        background-color: #333333 !important;
        border: 1px solid #444444 !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
    }
    
    button[kind="primary"] {
        color: #ffffff !important;
        background-color: #4CAF50 !important; /* Green background for primary button */
        border: 1px solid #388E3C !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
    }
    
    /* Alerts */
    [data-testid="stAlert"], [data-testid="stWarning"], [data-testid="stInfo"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #333333 !important;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    
    /* Info box in sidebar - About Project Samarth section */
    section[data-testid="stSidebar"] div[data-testid="stInfo"],
    section[data-testid="stSidebar"] .stInfo {
        color: #ffffff !important;
        background-color: #000000 !important;
        border: 1px solid #444444 !important;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    
    /* Custom About Project Samarth section */
    section[data-testid="stSidebar"] .about-section {
        color: #ffffff !important;
        background-color: #000000 !important;
        border: 1px solid #444444 !important;
        border-radius: 10px;
        padding: 1.5rem;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
        margin-bottom: 1rem;
    }
    
    /* Dataframes */
    .stDataFrame {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-size: 1.0rem !important;
    }
    
    /* Dataframe table */
    .stDataFrame table {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-size: 1.0rem !important;
    }
    
    .stDataFrame th {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
        border: 1px solid #dddddd !important;
        font-size: 1.0rem !important;
        font-weight: 600 !important;
    }
    
    .stDataFrame td {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #dddddd !important;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: #4CAF50 !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #333333 !important;
        font-size: 1.1rem !important;
    }
    
    [data-testid="stExpander"] * {
        color: #000000 !important;
        font-weight: 400 !important;
    }
    
    [data-testid="stExpander"] button {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* Markdown text */
    .stMarkdown {
        color: #cccccc !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    
    .stMarkdown h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    .stMarkdown h2 {
        font-size: 2.0rem !important;
        font-weight: 600 !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }
    
    /* Placeholder text */
    textarea[kind="text-input"]::placeholder {
        color: #666666 !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    
    /* Spinner */
    [data-testid="stSpinner"] {
        color: #cccccc !important;
    }
    
    [data-testid="stSpinner"] div {
        border-color: #333333 !important;
        border-top-color: transparent !important;
    }
    
    /* Button hover effects */
    button[kind="secondary"]:hover {
        background-color: #444444 !important;
    }
    
    button[kind="primary"]:hover {
        background-color: #388E3C !important; /* Darker green on hover */
    }
    
    /* Charts */
    .matplotlib-figure {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Main content headers */
    h3 {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        color: #aaaaaa !important;
    }
    
    /* New user tips styling */
    .new-user-tips {
        background-color: #222222 !important;
        border: 1px solid #444444;
        border-radius: 10px;
        padding: 1rem;
        color: #ffffff !important;
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    
    .new-user-tips strong {
        color: #4CAF50 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

def _create_matplotlib_chart(df, visualization_data):
    """Create matplotlib chart as fallback"""
    if len(df) > 1:
        try:
            # Try to create charts based on the data
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Create visualization container
                st.markdown("<div class='visualization-container'>", unsafe_allow_html=True)
                st.markdown("#### Data Visualization", unsafe_allow_html=True)
                
                # Dynamic chart generation based on data structure and chart type
                chart_type = visualization_data.get('chart_type', 'bar')
                
                # Bar chart: For data with categorical x-axis and numerical y-axis
                if chart_type == 'bar' and len(df.columns) >= 2:
                    # Determine x and y columns
                    x_col = df.columns[0]  # First column as x-axis
                    y_col = None
                    
                    # Find the first numerical column for y-axis
                    for col in df.columns[1:]:
                        if col in numeric_cols:
                            y_col = col
                            break
                    
                    if y_col:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        bars = ax.bar(df[x_col], df[y_col], color='#4CAF50')
                        ax.set_xlabel(str(x_col), fontsize=12, color='#000000')
                        ax.set_ylabel(str(y_col), fontsize=12, color='#000000')
                        ax.set_title(f'{y_col} by {x_col}', fontsize=14, color='#000000')
                        ax.tick_params(colors='#000000', labelsize=10)
                        ax.title.set_color('#000000')
                        ax.xaxis.label.set_color('#000000')
                        ax.yaxis.label.set_color('#000000')
                        fig.patch.set_facecolor('#ffffff')
                        ax.set_facecolor('#ffffff')
                        ax.grid(True, alpha=0.3, color='#cccccc')
                        
                        # Rotate x-axis labels if they are long
                        if df[x_col].astype(str).str.len().max() > 10:
                            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
                        
                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate(f'{height:.0f}' if height == int(height) else f'{height:.2f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),
                                        textcoords="offset points",
                                        ha='center', va='bottom',
                                        color='#000000',
                                        fontsize=10)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                
                # Line chart: For time series data
                elif chart_type == 'line' and len(df.columns) >= 2:
                    # Determine x and y columns
                    x_col = df.columns[0]  # First column as x-axis
                    y_col = None
                    
                    # Find the first numerical column for y-axis
                    for col in df.columns[1:]:
                        if col in numeric_cols:
                            y_col = col
                            break
                    
                    if y_col:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(df[x_col], df[y_col], marker='o', linewidth=2, markersize=6, color='#4CAF50')
                        ax.set_xlabel(str(x_col), fontsize=12, color='#000000')
                        ax.set_ylabel(str(y_col), fontsize=12, color='#000000')
                        ax.set_title(f'{y_col} Over Time', fontsize=14, color='#000000')
                        ax.grid(True, alpha=0.3, color='#cccccc')
                        ax.tick_params(colors='#000000', labelsize=10)
                        ax.title.set_color('#000000')
                        ax.xaxis.label.set_color('#000000')
                        ax.yaxis.label.set_color('#000000')
                        fig.patch.set_facecolor('#ffffff')
                        ax.set_facecolor('#ffffff')
                        
                        # Rotate x-axis labels if they are long
                        if df[x_col].astype(str).str.len().max() > 10:
                            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                
                # Pie chart: For composition data
                elif chart_type == 'pie' and len(df.columns) >= 2:
                    # Determine label and value columns
                    label_col = df.columns[0]  # First column as labels
                    value_col = None
                    
                    # Find the first numerical column for values
                    for col in df.columns[1:]:
                        if col in numeric_cols:
                            value_col = col
                            break
                    
                    if value_col:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        # Take top 10 items for better visualization
                        if len(df) > 10:
                            df_pie = df.nlargest(10, value_col)
                        else:
                            df_pie = df
                            
                        # Convert labels to list of strings
                        labels = df_pie[label_col].astype(str).tolist()
                        values = df_pie[value_col].tolist()
                        
                        pie_result = ax.pie(
                            values, 
                            labels=labels, 
                            autopct='%1.1f%%',
                            startangle=90
                        )
                        ax.set_title(f'Distribution of {value_col}', fontsize=14, color='#000000')
                        ax.axis('equal')
                        fig.patch.set_facecolor('#ffffff')
                        
                        # Improve text visibility if percentages are returned
                        if len(pie_result) > 2:
                            autotexts = pie_result[2]
                            for autotext in autotexts:
                                autotext.set_color('white')
                                autotext.set_fontweight('bold')
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                
                # Default to bar chart if no specific chart type
                elif len(df.columns) >= 2:
                    # Determine x and y columns
                    x_col = df.columns[0]  # First column as x-axis
                    y_col = None
                    
                    # Find the first numerical column for y-axis
                    for col in df.columns[1:]:
                        if col in numeric_cols:
                            y_col = col
                            break
                    
                    if y_col:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        bars = ax.bar(df[x_col], df[y_col], color='#4CAF50')
                        ax.set_xlabel(str(x_col), fontsize=12, color='#000000')
                        ax.set_ylabel(str(y_col), fontsize=12, color='#000000')
                        ax.set_title(f'{y_col} by {x_col}', fontsize=14, color='#000000')
                        ax.tick_params(colors='#000000', labelsize=10)
                        ax.title.set_color('#000000')
                        ax.xaxis.label.set_color('#000000')
                        ax.yaxis.label.set_color('#000000')
                        fig.patch.set_facecolor('#ffffff')
                        ax.set_facecolor('#ffffff')
                        ax.grid(True, alpha=0.3, color='#cccccc')
                        
                        # Rotate x-axis labels if they are long
                        if df[x_col].astype(str).str.len().max() > 10:
                            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
                        
                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate(f'{height:.0f}' if height == int(height) else f'{height:.2f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),
                                        textcoords="offset points",
                                        ha='center', va='bottom',
                                        color='#000000',
                                        fontsize=10)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                
                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.info("Could not generate visualization for this data.")

    else:
        st.warning("Please enter a question.")

# Main header
st.markdown("<h1 class='main-header'>Project Samarth 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='subheader'>Intelligent Q&A System for India’s Agricultural and Climate Insights</h3>", unsafe_allow_html=True)

# Information box about available data
st.markdown("<div class='info-box'><strong>Available Data:</strong> Based on our current dataset, we have agricultural production data for various Indian states from 2009-2015 and weather data for 2020. Please adjust your queries accordingly.</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("About Project Samarth")
    # Custom styled div for About Project Samarth section
    st.markdown("""
    <div class="about-section">
    Project Samarth is an AI-driven question-answering platform that enables natural language interaction with real government datasets from data.gov.in.

    It focuses on analyzing India's agricultural economy and its relationship with climate patterns.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("✨ Example Questions")
    
    # Display example questions for inspiration
    st.markdown("*Use these examples as inspiration for your own questions:*")
    
    example_questions = [
        "What was the crop production trend in Andhra Pradesh from 2010 to 2013?",
        "How does rainfall affect rice production in Assam?",
        "Which states received the highest rainfall in June 2020?",
        "How has cotton production changed in Gujarat over the past 5 years?",
        "Show me the top 5 crops by production in Madhya Pradesh in 2012"
    ]
    
    # Display example questions without auto-fill functionality
    for i, question in enumerate(example_questions, 1):
        st.markdown(f"<div class='example-question'><strong>📝 Example {i}:</strong><br>{question}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💡 Quick Tips")
    st.markdown("""
    - Be specific with time periods and locations
    - Ask about relationships between agriculture and climate
    - Try comparative questions between states or crops
    - Use natural language as you would in conversation
    """)

# Main content
st.markdown("### Ask a Question About Indian Agriculture & Climate")

# Information about examples with emoji for better visibility
st.markdown("<div class='new-user-tips'>💡 <strong>New Users:</strong> Check the sidebar for example questions to inspire your own queries!</div>", unsafe_allow_html=True)

# API endpoint
API_BASE_URL = os.getenv("API_BASE_URL", "http://samarthqasystem-production.up.railway.app")

# User input with session state
if 'question' not in st.session_state:
    st.session_state.question = ""
question = st.text_area(
    "Enter your question:",
    value=st.session_state.question,
    placeholder="e.g., What was the crop production trend in Andhra Pradesh from 2010 to 2013?",
    height=100,
    key="question_input"
)

# Clear button
col1, col2 = st.columns([1, 6])
with col1:
    if st.button("Clear"):
        st.session_state.question = ""
        st.rerun()
with col2:
    ask_button = st.button("Ask Samarth", type="primary")

if ask_button and question:
    if question:
        with st.spinner("Analyzing data and generating insights..."):
            try:
                # Make API request
                response = requests.post(
                    f"{API_BASE_URL}/query/ask",
                    json={"question": question},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display answer
                    st.markdown("### Answer")
                    st.markdown(f"<div class='response-box'>{result['answer']}</div>", unsafe_allow_html=True)
                    
                    # Display metrics in cards
                    st.markdown("### Metrics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("<div class='metric-card'><div class='metric-label'>Confidence Score</div><div class='metric-value'>{:.2%}</div></div>".format(result['confidence_score']), unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div class='metric-card'><div class='metric-label'>Execution Time</div><div class='metric-value'>{:.2f}s</div></div>".format(result['execution_time']), unsafe_allow_html=True)
                    with col3:
                        st.markdown("<div class='metric-card'><div class='metric-label'>Data Sources</div><div class='metric-value'>{}</div></div>".format(len(result['data_sources'])), unsafe_allow_html=True)
                    
                    # Display sample data with visualization
                    # Check if we have visualization data
                    visualization_data = result.get('visualization_data')
                    if visualization_data and isinstance(visualization_data, dict) and visualization_data.get('data'):
                        st.markdown("### Data Visualization")
                        
                        # Get chart type and data
                        chart_type = visualization_data.get('chart_type', 'bar')
                        chart_data = visualization_data.get('data', [])
                        
                        if chart_data and len(chart_data) > 0:
                            # Convert to DataFrame for visualization
                            df = pd.DataFrame(chart_data)
                            
                            # Display data table with dark theme styling
                            st.dataframe(df, width=st.session_state.get('dataframe_width', 'stretch'), height=300)
                            
                            # Use the visualization module to create the chart
                            try:
                                chart_base64 = create_visualization(chart_data, chart_type)
                                
                                if chart_base64:
                                    # Display the chart image
                                    st.markdown("<div class='visualization-container'>", unsafe_allow_html=True)
                                    st.markdown("#### Data Visualization", unsafe_allow_html=True)
                                    st.image(f"data:image/png;base64,{chart_base64}", use_column_width=True)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                else:
                                    # Fallback to matplotlib if visualization module fails
                                    _create_matplotlib_chart(df, visualization_data)
                            except Exception as viz_error:
                                st.info(f"Could not generate visualization: {str(viz_error)}")
                                # Still show the data
                                st.dataframe(df, width=st.session_state.get('dataframe_width', 'stretch'), height=300)
                        else:
                            st.info("No data available for visualization.")
                    else:
                        # Check if we have raw data in the result
                        raw_data = result.get('data', [])
                        if raw_data and len(raw_data) > 0:
                            # Try to create visualization from the main data
                            try:
                                df = pd.DataFrame(raw_data)
                                if len(df) > 0:
                                    st.markdown("### Data")
                                    st.dataframe(df, width=st.session_state.get('dataframe_width', 'stretch'), height=300)
                                else:
                                    st.info("No data available for display.")
                            except Exception as df_error:
                                st.info(f"Could not display data: {str(df_error)}")
                        else:
                            # Last resort: try to extract data from any available field
                            # Check if there are any list fields in the result that might contain data
                            data_fields = [key for key, value in result.items() if isinstance(value, list) and len(value) > 0]
                            found_data = False
                            for field in data_fields:
                                if field not in ['data_sources', 'sql_queries']:
                                    try:
                                        df = pd.DataFrame(result[field])
                                        if len(df) > 0:
                                            st.markdown(f"### {field.replace('_', ' ').title()}")
                                            st.dataframe(df, width=st.session_state.get('dataframe_width', 'stretch'), height=300)
                                            found_data = True
                                            break
                                    except Exception:
                                        continue
                            
                            if not found_data:
                                st.info("No additional data available for this query.")
                else:
                    st.error(f"API request failed with status code: {response.status_code}")
                    st.error(f"Response: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend service. Please make sure the backend is running and accessible.")
            except requests.exceptions.Timeout:
                st.error("Request to backend timed out. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")
# Footer
st.markdown("---")
st.markdown("<div class='footer'>Project Samarth - Empowering data-driven decision making for Indian agriculture and climate policy</div>", unsafe_allow_html=True)