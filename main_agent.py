# main_agent.py

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents and dependencies
from agents.data_analysis_agent import data_analysis_agent
from agents.policy_maker_agent import policy_agent # Note: Function name is policy_agent
from agents.visualizing_agent import visualization_agent # Note: Function name is visualization_agent
from agents.decider_agent import deciding_agent
import pandas as pd
from agents.user_agent import usy_agent
from llm_main import llm
import json

# Placeholder definition for deciding_agent if it's not in the file
# If deciding_agent is in a separate file, remove the placeholder below.
# I'll include the deciding_agent code in section 2 below.

class IngresAgent:
    def __init__(self, dataframe, query, role):
        self.df = dataframe
        self.context = {}
        self.query = query
        self.results = {}  # Store all agent results
        self.final_output = None 
        self.role = role # Store the final user-facing output

    def run_pipeline(self):
        """
        Executes the full pipeline and returns the appropriate output based on agents run.
        """
        agent_list = deciding_agent(self.query, self.role)
        
        # Safety check for NoneType error (from previous feedback)
        if agent_list is None:
            agent_list = []
            print("--- WARNING: deciding_agent returned None. No agents will run. ---")
            
        print(f"\n--- Agents to Run: {agent_list} ---")

        for agent_name in agent_list:
            if agent_name == "data_analysis_agent":
                print("\n--- Data Analysis ---")
                analysis = data_analysis_agent(self.df, self.query)
                self.context['data_analysis'] = analysis
                self.results['data_analysis'] = analysis
                print(analysis)

            # 🛑 CORRECTED: Changed "create_research_agent" to "policy_agent" 
            # to match the consistent name in deciding_agent (see section 2)
            elif agent_name == "policy_agent":
                print("\n Policy Agent ---")
                policy = policy_agent(self.query, self.context)
                self.context['policy'] = policy
                self.results['policy'] = policy
                print(policy)

            # 🛑 CORRECTED: Changed "create_visualization_points" to "visualization_agent" 
            # to match the consistent name in deciding_agent (see section 2)
            elif agent_name == "visualization_agent":
                print("\n Creating Visualization Points ---")
                visualization = visualization_agent(self.df,self.query, self.context)
                self.context['visualization'] = visualization
                self.results['visualization'] = visualization
                print(visualization)

            elif agent_name == "user_agent":
                print("\n User Agent ---")
                user_ans = usy_agent(self.query, self.context)
                self.context['user_ans'] = user_ans
                self.results['user_ans'] = user_ans
                print(user_ans)
            
            else:
                print(f"Unknown agent: {agent_name}")
        
        # Determine the final output based on what was generated
        self.final_output = self._determine_final_output(agent_list)
        return self.final_output

    def _determine_final_output(self, agent_list):
        """
        Determines what to return based on the agents that were executed.
        Priority: policy > user_agent > data_analysis > visualization
        """
        # If policy ran (key: 'policy'), return policy output
        if 'policy' in self.results:
            return self.results['policy']
        
        # 🛑 CORRECTED: Changed key check from 'user_agent' to the correct storage key 'user_ans'
        if 'user_ans' in self.results:
            return self.results['user_ans']
        
        # If only data analysis ran, return that
        if 'data_analysis' in self.results:
            return self.results['data_analysis']
        
        # If only visualization ran, return visualization data
        if 'visualization' in self.results:
            return self.results['visualization']
        
        # Fallback: return all results
        return self.results

    def get_all_results(self):
        """
        Returns all intermediate results for debugging or detailed analysis.
        """
        return self.results

    def get_context(self):
        """
        Returns the full context for inspection.
        """
        return self.context

if __name__ == "__main__":
    # Ensure ingres_one.csv exists for this to run
    try:
        df = pd.read_csv('ingres_one.csv')
    except FileNotFoundError:
        print("ERROR: Please create a dummy 'ingres_one.csv' file for the example to run.")
        sys.exit(1)
        
    query = "Tell me the water extraction levels of all districts in Assam with help of graph"
    role = 'citizen'
    
    respy = IngresAgent(df, query, role)
    
    # Corrected: Call run_pipeline() to execute the logic
    final_result = respy.run_pipeline() 
    print("\n--- Final Output ---")
    print(final_result)
    print(respy.results['visualization'])