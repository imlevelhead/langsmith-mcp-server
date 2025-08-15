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


def fetch_trace_tool(client, project_name: str = None, trace_id: str = None) -> Dict[str, Any]:
    """
    Fetch the trace content for a specific project or specify a trace ID.

    Note: Only one of the parameters (project_name or trace_id) is required.
    trace_id is preferred if both are provided.

    Args:
        client: LangSmith client instance
        project_name: The name of the project to fetch the last trace for
        trace_id: The ID of the trace to fetch (preferred parameter)

    Returns:
        Dictionary containing the last trace and metadata
    """
    # Handle None values and "null" string inputs
    if project_name == "null":
        project_name = None
    if trace_id == "null":
        trace_id = None

    if not project_name and not trace_id:
        return {"error": "Error: Either project_name or trace_id must be provided."}

    try:
        # Get the last run
        runs = client.list_runs(
            project_name=project_name if project_name else None,
            id=[trace_id] if trace_id else None,
            select=[
                "inputs",
                "outputs",
                "run_type",
                "id",
                "error",
                "total_tokens",
                "total_cost",
                "feedback_stats",
                "app_path",
                "thread_id",
            ],
            is_root=True,
            limit=1
        )

        runs = list(runs)

        if not runs or len(runs) == 0:
            return {"error": "No runs found for project_name: {}".format(project_name)}

        run = runs[0]

        # Return just the trace ID as we can use this to open the trace view
        return {
            "trace_id": str(run.id),
            "run_type": run.run_type,
            "id": str(run.id),
            "error": run.error,
            "inputs": run.inputs,
            "outputs": run.outputs,
            "total_tokens": run.total_tokens,
            "total_cost": str(run.total_cost),
            "feedback_stats": run.feedback_stats,
            "app_path": run.app_path,
            "thread_id": str(run.thread_id) if hasattr(run, "thread_id") else None,
        }
    except Exception as e:
        return {"error": f"Error fetching last trace: {str(e)}"}
    


if __name__ == "__main__":
    result = fetch_trace_tool(client, trace_id="1f079507-20f7-6735-ba6f-db9d6cc0f733")
    output_path = os.path.join(os.path.dirname(__file__), "trace_result.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    print(f"Trace saved to {output_path}")