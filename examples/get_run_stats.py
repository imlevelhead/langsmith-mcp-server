from typing import Any, Dict

import os
import sys
import json

from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LANGSMITH_API_KEY")

client = Client(api_key=api_key)


# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

def get_project_runs_stats_tool(
    client,
    project_name: str = None,
    trace_id: str = None,
) -> Dict[str, Any]:
    """
    Get the project runs stats. 

    Note: Only one of the parameters (project_name or trace_id) is required.
    trace_id is preferred if both are provided.

    Args:
        client: LangSmith client instance
        project_name: The name of the project to fetch the runs stats for
        trace_id: The ID of the trace to fetch (preferred parameter)

    Returns:
        Dictionary containing the project runs stats
    """
    # Handle None values and "null" string inputs
    if project_name == "null":
        project_name = None
    if trace_id == "null":
        trace_id = None

    if not project_name and not trace_id:
        return {"error": "Error: Either project_name or trace_id must be provided."}

    try:
        # Break down the qualified project name
        parts = project_name.split("/")
        is_qualified = len(parts) == 2
        actual_project_name = parts[1] if is_qualified else project_name

        # Get the project runs stats
        project_runs_stats = client.get_run_stats(
            project_names=[actual_project_name] if project_name else None,
            trace=trace_id if trace_id else None,
        )
        # remove the run_facets from the project_runs_stats
        project_runs_stats.pop("run_facets", None)
        # add project_name to the project_runs_stats
        project_runs_stats["project_name"] = actual_project_name
        return project_runs_stats
    except Exception as e:
        return {"error": f"Error getting project runs stats: {str(e)}"}
    

if __name__ == "__main__":
    result = get_project_runs_stats_tool(client, project_name="chat-langchain-v3")
    output_path = os.path.join(os.path.dirname(__file__), "run_stats_result.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    print(f"Run stats saved to {output_path}")