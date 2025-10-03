import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_main import llm

def policy_agent(query, context):
    """
    Creates policy recommendations based on data analysis.
    
    Args:
        query: User's question about groundwater
        context: Optional additional context (not used currently)
    
    Returns:
        str: Policy recommendations and summary
    """
    try:
       
        data_analysis = context.get('data_analysis', 'No analysis available.')
        
        
        prompt = f"""
                    You are a policy advisor for groundwater management in India.

                    DATA ANALYSIS RESULTS:
                    {data_analysis}

                    ORIGINAL QUERY:
                    {query}

                    YOUR TASK:
                    Write a concise policy brief (under 250 words) for government officials who will create policy based on your recommendations.

                    STRUCTURE YOUR RESPONSE AS FOLLOWS:

                    **EXECUTIVE SUMMARY** (5-6 sentences)
                    [Key findings from the data analysis]

                    **CRITICAL FINDINGS**
                    - [Most important data point 1]
                    - [Most important data point 2]
                    - [Most important data point 3]

                    **POLICY RECOMMENDATIONS**
                    1. [Immediate action required]
                    2. [Medium-term intervention]
                    3. [Long-term strategy]

                    **SUGGESTED ACTIONS**
                    - [Specific, actionable step 1]
                    - [Specific, actionable step 2]
                    - [Specific, actionable step 3]

                    IMPORTANT:
                    - Be specific and data-driven
                    - Include exact numbers from the analysis
                    - Don't miss any critical points from the data
                    - Make recommendations actionable and realistic
                    - Consider economic and social impacts
                    - Prioritize urgent issues

                    Write the policy brief now.
"""
        
        policy_response = llm.invoke(prompt)
        return policy_response.content
    
    except Exception as e:
        error_msg = f"Error generating policy recommendations: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

