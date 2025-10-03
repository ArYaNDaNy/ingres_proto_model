from flask import Flask, request, jsonify
import pandas as pd
import json
import sys
import os
# Ensure the path is set correctly for imports in main_agent.py and the agents
# NOTE: Adjusted path logic slightly for better compatibility if app.py is run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

# 🛑 IMPORT THE MAIN AGENT CLASS
try:
    from main_agent import IngresAgent
except ImportError:
    print("ERROR: Could not import IngresAgent from main_agent.py. Check your paths.")
    sys.exit(1)


# 1. Initialize Flask App
app = Flask(__name__)

# 2. Load Data Once on Application Startup
# This is crucial for performance: DO NOT load the CSV inside the route function.
try:
    GLOBAL_DF = pd.read_csv('ingres_one.csv')
    print("✅ DataFrame 'ingres_one.csv' loaded successfully.")
except FileNotFoundError:
    print("FATAL ERROR: 'ingres_one.csv' not found. Please ensure it is in the correct directory.")
    GLOBAL_DF = None # Set to None to prevent crashes later
except Exception as e:
    print(f"FATAL ERROR: Failed to load DataFrame: {e}")
    GLOBAL_DF = None


# 3. Define the API Route for Agent Execution
@app.route('/api/run_agent', methods=['POST'])
def run_agent_pipeline():
    """
    Receives query and role, executes the IngresAgent pipeline, 
    and returns the final output combined with visualization data.
    """
    if GLOBAL_DF is None:
        return jsonify({"error": "Data server is unavailable. Failed to load 'ingres_one.csv'."}), 503

    # Check for JSON data
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload in request."}), 400

    # Extract required parameters
    query = data.get('query')
    role = data.get('role')

    if not query or not role:
        return jsonify({"error": "Missing 'query' or 'role' parameter in the request."}), 400

    try:
        # Initialize and run the IngresAgent pipeline
        agent_instance = IngresAgent(
            dataframe=GLOBAL_DF,
            query=query,
            role=role
        )
        final_output = agent_instance.run_pipeline()

        # --- 🛑 CORRECTED LOGIC TO INCLUDE VISUALIZATION CONTEXT ---
        
        # 1. Safely extract the visualization data (it will be None if the agent didn't run)
        viz_data = agent_instance.results.get('visualization', None)
        
        # 2. Structure the combined response dictionary
        response_data = {
            "query": query,
            "role": role,
            "visualization_context": viz_data,
            "main_output": None
        }

        # 3. Handle the main_output (which could be a string summary or a structured dict)
        if isinstance(final_output, dict):
            # If the final_output is already a dict (e.g., pure data analysis or visualization output)
            response_data["main_output"] = final_output
        elif isinstance(final_output, str):
            # If it's a string (e.g., user_agent or policy_agent summary), wrap it
            response_data["main_output"] = {"summary_text": final_output}
        else:
            # Catchall
            response_data["main_output"] = {"summary_text": str(final_output)}
            
        return jsonify(response_data), 200
        # --- END CORRECTED LOGIC ---

    except Exception as e:
        print(f"An unexpected error occurred during pipeline execution: {e}")
        # Print traceback for better debugging on the server side
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error during agent execution: {str(e)}"}), 500


# 4. Run the Application
if __name__ == '__main__':
    # Flask runs on http://127.0.0.1:5000/ by default
    app.run(debug=True)
