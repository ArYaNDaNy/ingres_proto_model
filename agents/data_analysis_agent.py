import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_main import llm
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Load CSV once globally
df = pd.read_csv('../ingres_one.csv')


def query_maker(query):
    """Optimizes user query for pandas agent by identifying relevant columns."""
    try:
        columns = df.columns.tolist()
        
        prompt = f"""
                    You are a query optimizer for groundwater data analysis.

                    Available columns in the dataset:
                    {columns}

                    User's original query: "{query}"

                    Your task:
                    1. Identify which specific columns from the list above are relevant to the user's query
                    2. Rewrite the query to be more specific and optimized for a pandas data analysis agent
                    3. Include exact column names in the optimized query
                    4. Make the query actionable and clear

                    Example:
                    Original: "Give me groundwater comparison between ground water extraction of pune and mumbai"
                    Optimized: "Compare the 'Ground Water Extraction for all uses (ha.m)' between districts where DISTRICT is 'Pune' and 'Mumbai', showing STATE, DISTRICT, and the extraction values"

                    Return ONLY the optimized query as a string, nothing else.
                    """
        
        opt_query = llm.invoke(prompt)
        return opt_query.content.strip()
    
    except FileNotFoundError:
        return f"Error: CSV file not found at '../ingres_one.csv'"
    except Exception as e:
        return f"Error optimizing query: {str(e)}"




def data_analysis_agent(query, max_retries=3):
    """Creates a data analysis agent with custom instructions."""
    opt_query = query_maker(query)
    
    print(f"Original Query: {query}")
    print(f"Optimized Query: {opt_query}\n")
    
    AGENT_PREFIX = f"""You are an expert data analyst specializing in groundwater resources analysis using pandas.

CONTEXT:
- You have access to a groundwater dataset with {len(df)} records and {len(df.columns)} columns
- User's optimized query: "{opt_query}"

YOUR RESPONSIBILITIES:
1. Convert the user query into efficient pandas operations
2. Perform comprehensive data analysis including:
   - Statistical summaries (mean, median, std, min, max)
   - Comparisons and trends
   - Grouping and aggregations where relevant
   - Data quality checks (missing values, outliers)
3. Extract maximum insights from the data
4. Present findings in a clear, structured format

IMPORTANT NOTES:
- Your analysis will be used by downstream agents (visualization, policy recommendation, etc.)
- Be thorough and include all relevant metrics
- Always validate data before analysis (check for NaN, data types)
- If comparing regions, include percentage differences and rankings
- Round numerical outputs to 2 decimal places for readability

OUTPUT FORMAT:
Provide your analysis in this structure:
1. **Data Overview**: Brief summary of filtered/analyzed data
2. **Key Findings**: Main insights with numbers
3. **Detailed Analysis**: Breakdown by categories if applicable
4. **Recommendations**: What the data suggests

Begin your analysis now.
"""

    agent_executor = create_pandas_dataframe_agent(
        llm=llm,
        df=df,
        prefix=AGENT_PREFIX,
        verbose=True,
        allow_dangerous_code=True,
        agent_type="openai-functions",
    )
    
    # Retry logic for API errors
    for attempt in range(max_retries):
        try:
            result = agent_executor.invoke({"input": opt_query})
            return result
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
            raise
    


