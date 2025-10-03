# agents/decider_agent.py (or wherever deciding_agent is defined)

import json
# Assuming llm_main is available
from llm_main import llm 
from textwrap import dedent


def deciding_agent(query: str, role: str) -> list:
    """
    Uses an LLM to decide which agents to run in what order based on query and user role.
    
    Args:
        query: User's question about groundwater
        role: User's role (e.g., 'government', 'researcher', 'citizen')
    
    Returns:
        list: Ordered list of agent names to execute
    """
    
    # 🛑 CORRECTED: Renamed keys to match the actual function names used in main_agent.py
    AGENT_DEFINITIONS = {
        "data_analysis_agent": "Analyzes groundwater extraction CSV data including rainfall, recharge, extraction rates, and stage of extraction. Use this as the FIRST agent for almost all groundwater-related queries to get comprehensive data insights.",
        
        "policy_agent": "Generates concise policy briefs and recommendations for government officials. Use when role='government' OR when user asks for policy recommendations, government actions, or administrative decisions. Provides actionable suggestions based on data analysis.",
        
        "visualization_agent": "Creates structured JSON data for charts and graphs (bar charts, line charts, pie charts, maps). Use ONLY when user explicitly requests a 'chart', 'graph', 'visualization', 'plot', or 'show me visually'.",
        
        "user_agent": "Provides simplified, citizen-friendly summaries for general public. Use when role='citizen' OR when user needs easy-to-understand explanations without technical jargon. Focuses on practical implications for common people."
    }
    
    # Create readable tools description
    tools_description = "\n".join(
        f"- **{name}**: {desc}" 
        for name, desc in AGENT_DEFINITIONS.items()
    )

    prompt = dedent(f"""
                        You are an expert router agent for a groundwater management system. Your job is to analyze the user's query and their role, then determine which agents should run and in what sequence.

                        **USER INFORMATION:**
                        - Query: "{query}"
                        - Role: {role}

                        **AVAILABLE AGENTS:**
                        {tools_description}

                        **ROUTING RULES:**

                        1. **Data Analysis First**: Almost always start with `data_analysis_agent` to fetch and analyze data
                        
                        2. **Role-Based Routing**:
                        - If role is "government" → use `policy_agent` for final summary
                        - If role is "citizen" or "user" → use `user_agent` for final summary
                        - If role is "researcher" → only use `data_analysis_agent` (detailed output)

                        3. **Visualization Rules**:
                        - ONLY include `visualization_agent` if query contains words like: "chart", "graph", "plot", "visualize", "show graph", "create chart"
                        - Visualization should come AFTER data analysis
                        - Examples requiring visualization: "show me a chart", "plot the data", "graph the comparison"

                        4. **Query Pattern Examples (Using Corrected Agent Names)**:
                        - "Compare groundwater in X and Y" → ["data_analysis_agent", "policy_agent"] (if role=government)
                        - "Show chart of rainfall" → ["data_analysis_agent", "visualization_agent"]
                        - "Which blocks are over-exploited?" → ["data_analysis_agent", "user_agent"] (if role=citizen)
                        - "Give policy recommendations" → ["data_analysis_agent", "policy_agent"]

                        **YOUR TASK:**
                        Return ONLY a JSON array of agent names in execution order. No explanations, no markdown, no extra text.

                        **Response Format:**
                        ["agent_name_1", "agent_name_2", ...]

                        **Examples:**

                        Query: "Compare groundwater extraction in Punjab and Haryana"
                        Role: government
                        Response: ["data_analysis_agent", "policy_agent"]

                        Query: "Show me a bar chart of rainfall data"
                        Role: citizen
                        Response: ["data_analysis_agent", "visualization_agent"]

                        Query: "Which districts have critical groundwater levels?"
                        Role: citizen
                        Response: ["data_analysis_agent", "user_agent"]

                        Query: "Analyze groundwater recharge patterns"
                        Role: researcher
                        Response: ["data_analysis_agent"]

                        Now process the user's query and return the agent sequence:
                        """)

    try:
        # ⚠️ NOTE: This requires a functional LLM implementation in llm_main.py
        response = llm.invoke(prompt) 
        
        if hasattr(response, 'content'):
            response_str = response.content
        else:
            response_str = str(response)
        
        # Clean and parse JSON
        clean_str = response_str.strip()
        
        # Robustly handle markdown code fences
        if "```json" in clean_str:
            clean_str = clean_str.split("```json")[1].split("```")[0]
        elif "```" in clean_str:
            clean_str = clean_str.split("```")[1].split("```")[0]
        
        clean_str = clean_str.strip()
        
        # Parse JSON
        agent_list = json.loads(clean_str)
        
        # Validate it's a list
        if isinstance(agent_list, list):
            # Validate agent names
            valid_agents = set(AGENT_DEFINITIONS.keys())
            validated_list = [
                agent for agent in agent_list 
                if agent in valid_agents
            ]
            # 🛑 Ensure a list is always returned
            return validated_list 
        else:
            print(f"⚠️ LLM returned non-list JSON: {agent_list}")
            # Fallback for invalid structure
            return ["data_analysis_agent"]
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: '{response_str}'")
        # Default fallback on parse error
        return ["data_analysis_agent"]
    
    except Exception as e:
        print(f"❌ Unexpected error in deciding_agent: {e}")
        # Default fallback on any other error (e.g., llm.invoke failure)
        return ["data_analysis_agent"]