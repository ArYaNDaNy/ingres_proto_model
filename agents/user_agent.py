import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_main import llm

def usy_agent(query, context):
    """
    Creates basic analysis for normal users based on data analysis.
    
    Args:
        query: User's question about groundwater
        context: Optional additional context (not used currently)
    
    Returns:
        str: summary
    """
    try:
        # Get data analysis result
        data_analysis = context.get('data_analysis', 'No analysis available.')
        
        prompt = f"""
                    You are an expert groundwater policy advisor helping farmers and citizens in India understand complex groundwater data in a simple, practical way.

                    Below is the data analysis and the user's query:

                    DATA ANALYSIS:
                    {data_analysis}

                    USER QUERY:
                    {query}

                    TASK:
                    Write a clear, data-driven policy brief (under 250 words) tailored for non-technical audiences such as farmers, rural communities, or local decision-makers.

                    RESPONSE STRUCTURE:

                    **EXECUTIVE SUMMARY (5-6 sentences)**  
                    - Summarize the key findings from the data in plain language.  
                    - Explain technical terms with simple examples.  
                    - Emphasize why this information matters for everyday life.

                    **CRITICAL FINDINGS**  
                    List the 3 most important, data-backed findings. Each should highlight a specific number, trend, or insight.  
                    - Point 1  
                    - Point 2  
                    - Point 3

                    **PERSONAL RECOMMENDATIONS (If applicable)**  
                    Include only if the user query involves investment, land use, or personal planning.  
                    1. Immediate Action  
                    2. Medium-Term Intervention  
                    3. Long-Term Strategy

                    **SUGGESTED ACTIONS**  
                    Give 3 specific, realistic, and locally relevant steps that individuals, communities, or local bodies can take based on the data.  
                    - Step 1  
                    - Step 2  
                    - Step 3

                    GUIDELINES:
                    - Be specific, use exact figures from the data.  
                    - Prioritize urgency and impact.  
                    - Avoid jargon — keep it farmer-friendly.  
                    - Make the brief sound practical, not academic.
                    """

        
        user_response = llm.invoke(prompt)
        return user_response.content
    
    except Exception as e:
        error_msg = f"Error generating policy recommendations: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


