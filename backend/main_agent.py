# main_agent.py

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents and dependencies
from agents.data_analysis_agent import data_analysis_agent
from agents.policy_maker_agent import policy_agent 
from agents.visualizing_agent import visualization_agent
from agents.decider_agent import deciding_agent
import pandas as pd
from agents.user_agent import usy_agent
from llm_main import llm
import json


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
        # NOTE: deciding_agent must be importable here
        agent_list = deciding_agent(self.query, self.role)
        
        # Safety check for NoneType error
        if agent_list is None:
            agent_list = []
            print("--- WARNING: deciding_agent returned None. No agents will run. ---")
            
        print(f"\n--- Agents to Run: {agent_list} ---")

        for agent_name in agent_list:
            if agent_name == "data_analysis_agent":
                print("\n--- Data Analysis ---")
                # NOTE: data_analysis_agent must be importable here
                analysis = data_analysis_agent(self.df, self.query)
                self.context['data_analysis'] = analysis
                self.results['data_analysis'] = analysis
                print(analysis)

            elif agent_name == "policy_agent":
                print("\n Policy Agent ---")
                policy = policy_agent(self.query, self.context)
                self.context['policy'] = policy
                self.results['policy'] = policy
                print(policy)

            elif agent_name == "visualization_agent":
                print("\n Creating Visualization Points ---")
                # Correctly passing self.df to visualization_agent
                visualization = visualization_agent(self.df, self.query, self.context)
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
        
        # Checking for the correct key 'user_ans'
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
# Note: The if __name__ == "__main__": block is removed or commented out 
# to allow clean import of IngresAgent into app.py