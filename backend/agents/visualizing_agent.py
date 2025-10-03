# visualization_agent.py

import sys
import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_main import llm


# 🛑 FIX: Added df argument
def extract_query_parameters(df: pd.DataFrame, query: str) -> Dict[str, Any]:
    """
    Uses LLM ONLY to extract filter parameters from query.
    NO agent execution - just parameter extraction.
    """
    prompt = f"""
    Extract filtering parameters from this groundwater query.
    
    Available columns in dataset:
    {df.columns.tolist()}
    
    User Query: "{query}"
    
    Return ONLY a valid JSON object with these keys:
    {{
        "states": ["list of state names in UPPERCASE if mentioned, or empty array"],
        "districts": ["list of district names if mentioned, or empty array"],
        "years": [list of years as integers, or empty array],
        "stage_filter": {{
            "type": "over-exploited/critical/semi-critical/safe/none",
            "min": number or null,
            "max": number or null
        }},
        "columns_to_show": ["list of column names to display from available columns"],
        "sort_by": "column name or null",
        "sort_order": "asc or desc",
        "limit": number or null
    }}
    
    CRITICAL RULES:
    - State names MUST be in UPPERCASE (e.g., "PUNJAB", "HARYANA", "RAJASTHAN")
    - over-exploited: Stage > 100
    - critical: Stage 90-100
    - semi-critical: Stage 70-90
    - safe: Stage < 70
    - Use EXACT column names from the available columns list
    - Always include STATE, DISTRICT, YEAR in columns_to_show
    
    Return ONLY valid JSON, no explanation.
    """
    
    # ... (LLM invocation and JSON parsing logic remains the same)
    response = llm.invoke(prompt)
    
    try:
        content = response.content.strip()
        
        # Remove markdown code fences properly
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        
        content = content.strip()
        
        # Additional cleanup: find JSON object boundaries
        if '{' in content and '}' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            content = content[start:end]

        params = json.loads(content)
        
        # FORCE UPPERCASE STATE NAMES (safety check)
        if params.get('states'):
            params['states'] = [state.upper() for state in params['states']]
        
        # FORCE UPPERCASE DISTRICT NAMES (safety check)
        if params.get('districts'):
            params['districts'] = [district.upper() for district in params['districts']]
        
        return params
    
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing error: {e}")
        # Default fallback
        return {
            "states": [],
            "districts": [],
            "years": [],
            "stage_filter": {"type": "none", "min": None, "max": None},
            "columns_to_show": ["STATE", "DISTRICT", "YEAR"],
            "sort_by": None,
            "sort_order": "desc",
            "limit": 20
        }
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        # Default fallback
        return {
            "states": [],
            "districts": [],
            "years": [],
            "stage_filter": {"type": "none", "min": None, "max": None},
            "columns_to_show": ["STATE", "DISTRICT", "YEAR"],
            "sort_by": None,
            "sort_order": "desc",
            "limit": 20
        }


# 🛑 FIX: Added df argument
def build_pandas_filters(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """
    Builds filters using PURE PANDAS operations.
    NO AGENTS - just direct DataFrame filtering.
    """
    filtered_df = df.copy() 
    
    # Filter by states (case-insensitive matching)
    if params.get('states') and len(params['states']) > 0:
        states_upper = [s.upper() for s in params['states']]
        filtered_df = filtered_df[filtered_df['STATE'].str.upper().isin(states_upper)]
    
    # Filter by districts (case-insensitive matching)
    if params.get('districts') and len(params['districts']) > 0:
        districts_upper = [d.upper() for d in params['districts']]
        filtered_df = filtered_df[filtered_df['DISTRICT'].str.upper().isin(districts_upper)]
    
    # Filter by years
    if params.get('years') and len(params['years']) > 0:
        filtered_df = filtered_df[filtered_df['YEAR'].isin(params['years'])]
    
    # Filter by stage (over-exploited, critical, etc.)
    stage_filter = params.get('stage_filter', {})
    stage_type = stage_filter.get('type', 'none')
    
    if stage_type == 'over-exploited':
        filtered_df = filtered_df[filtered_df['Stage of Ground Water Extraction (%)'] > 100]
    elif stage_type == 'critical':
        filtered_df = filtered_df[
            (filtered_df['Stage of Ground Water Extraction (%)'] >= 90) &
            (filtered_df['Stage of Ground Water Extraction (%)'] <= 100)
        ]
    elif stage_type == 'semi-critical':
        filtered_df = filtered_df[
            (filtered_df['Stage of Ground Water Extraction (%)'] >= 70) &
            (filtered_df['Stage of Ground Water Extraction (%)'] < 90)
        ]
    elif stage_type == 'safe':
        filtered_df = filtered_df[filtered_df['Stage of Ground Water Extraction (%)'] < 70]
    elif stage_filter.get('min') is not None:
        filtered_df = filtered_df[filtered_df['Stage of Ground Water Extraction (%)'] >= stage_filter['min']]
    
    if stage_filter.get('max') is not None:
        filtered_df = filtered_df[filtered_df['Stage of Ground Water Extraction (%)'] <= stage_filter['max']]
    
    return filtered_df


def select_and_format_columns(filtered_df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    # ... (Function body remains the same)
    columns = params.get('columns_to_show', [])
    
    # Validate columns exist
    valid_columns = [col for col in columns if col in filtered_df.columns]
    
    if not valid_columns:
        # Default columns
        valid_columns = ['STATE', 'DISTRICT', 'YEAR', 'Ground Water Extraction for all uses (ha.m)', 
                         'Stage of Ground Water Extraction (%)']
        valid_columns = [col for col in valid_columns if col in filtered_df.columns]
    
    # Select columns
    result_df = filtered_df[valid_columns].copy()
    
    # Round all numeric columns
    numeric_cols = result_df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if col != 'YEAR':
            result_df[col] = result_df[col].round(2)
    
    return result_df


def sort_and_limit_data(result_df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    # ... (Function body remains the same)
    # Sort
    sort_by = params.get('sort_by')
    if sort_by and sort_by in result_df.columns:
        ascending = (params.get('sort_order', 'desc') == 'asc')
        result_df = result_df.sort_values(by=sort_by, ascending=ascending)
    
    # Limit
    limit = params.get('limit')
    if limit and isinstance(limit, int) and limit > 0:
        result_df = result_df.head(limit)
    
    return result_df


def clean_column_names(columns: List[str]) -> Dict[str, str]:
    # ... (Function body remains the same)
    mapping = {
        'YEAR': 'year',
        'STATE': 'state',
        'DISTRICT': 'district',
        'Rainfall (mm)': 'rainfall_mm',
        'Ground Water Extraction for all uses (ha.m)': 'gw_extraction_ham',
        'Stage of Ground Water Extraction (%)': 'extraction_stage_percent',
        'Annual Extractable Ground water Resource (ham)': 'extractable_resource_ham',
        'Annual Ground water Recharge (ham)': 'annual_recharge_ham',
        'Net Annual Ground Water Availability for Future Use (ham)': 'future_availability_ham',
        'Ground Water Extraction for all uses (ha.m) - Domestic.3': 'domestic_extraction_ham',
        'Ground Water Extraction for all uses (ha.m) - Industrial.3': 'industrial_extraction_ham',
        'Ground Water Extraction for all uses (ha.m) - Irrigation.3': 'irrigation_extraction_ham',
        'Environmental Flows (ham)': 'environmental_flows_ham',
        'Total Geographical Area (ha)': 'total_geographical_area_ha',
        'Ground Water Recharge (ham)': 'gw_recharge_ham',
    }
    
    result = {}
    for col in columns:
        if col in mapping:
            result[col] = mapping[col]
        else:
            # Auto-generate clean name
            clean = col.lower()
            clean = clean.replace(' ', '_').replace('(', '').replace(')', '')
            clean = clean.replace('.', '').replace('-', '_') 
            result[col] = clean.strip('_')
    
    return result

def convert_to_json(result_df: pd.DataFrame, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
    # ... (Function body remains the same)
    if result_df.empty:
        return {
            "success": False,
            "query": query,
            "message": "No data found matching the query criteria",
            "data": [],
            "metadata": {
                "total_records": 0,
                "filters_applied": {
                    "states": params.get('states', []),
                    "years": params.get('years', []),
                    "stage_filter": params.get('stage_filter', {}).get('type', 'none')
                }
            }
        }
    
    # Clean column names
    column_mapping = clean_column_names(result_df.columns.tolist())
    result_df = result_df.rename(columns=column_mapping)
    
    # Convert to JSON using pure pandas
    data = result_df.to_dict(orient='records')
    
    return {
        "success": True,
        "query": query,
        "data": data,
        "metadata": {
            "total_records": len(data),
            "columns": list(result_df.columns),
            "filters_applied": {
                "states": params.get('states', []),
                "districts": params.get('districts', []),
                "years": params.get('years', []),
                "stage_filter": params.get('stage_filter', {}).get('type', 'none')
            }
        }
    }


# 🛑 FIX: Updated signature to accept df as the first argument
def visualization_agent(df: pd.DataFrame, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    MAIN FUNCTION: Pure pandas visualization agent.
    ...
    """
    print(f"\n{'='*80}")
    print(f"VISUALIZATION AGENT - 100% PURE PANDAS (NO AGENTS)")
    print(f"{'='*80}")
    print(f"Query: {query}\n")
    
    try:
        # Step 1: Extract parameters (LLM only for understanding)
        print("Step 1: Extracting query parameters...")
        # 🛑 FIX: Pass the DataFrame (df)
        params = extract_query_parameters(df, query)
        print(f"✓ Parameters: {json.dumps(params, indent=2)}\n")
        
        # Step 2: Filter data (PURE PANDAS)
        print("Step 2: Filtering data with pandas...")
        # 🛑 FIX: Pass the DataFrame (df)
        filtered_df = build_pandas_filters(df, params)
        print(f"✓ Filtered: {filtered_df.shape[0]} rows\n")
        
        # Step 3: Select and format columns (PURE PANDAS)
        print("Step 3: Selecting columns with pandas...")
        result_df = select_and_format_columns(filtered_df, params)
        print(f"✓ Selected: {result_df.shape[1]} columns\n")
        
        # Step 4: Sort and limit (PURE PANDAS)
        print("Step 4: Sorting and limiting with pandas...")
        result_df = sort_and_limit_data(result_df, params)
        print(f"✓ Final: {result_df.shape[0]} rows\n")
        
        # Step 5: Convert to JSON (PURE PANDAS to_dict)
        print("Step 5: Converting to JSON with pandas.to_dict()...")
        json_output = convert_to_json(result_df, query, params)
        print(f"✓ JSON generated: {len(json_output['data'])} records\n")
        print(f"{'='*80}\n")
        
        return json_output
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "data": []
        }