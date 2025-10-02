"""Tools for interacting with LangSmith traces and conversations."""

from typing import Any, Dict


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
            limit=1,
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


def get_thread_history_tool(client, thread_id: str, project_name: str) -> Dict[str, Any]:
    """
    Get the history for a specific thread.

    Args:
        client: LangSmith client instance
        thread_id: The ID of the thread to fetch history for
        project_name: The name of the project containing the thread

    Returns:
        A dictionary containing a list of messages in the thread history or an error.
    """
    try:
        # Filter runs by the specific thread and project
        filter_string = (
            f'and(in(metadata_key, ["session_id","conversation_id","thread_id"]), '
            f'eq(metadata_value, "{thread_id}"))'
        )

        # Only grab the LLM runs
        runs = [
            r
            for r in client.list_runs(
                project_name=project_name, filter=filter_string, run_type="llm"
            )
        ]

        if not runs or len(runs) == 0:
            return {"error": f"No runs found for thread {thread_id} in project {project_name}"}

        # Sort by start time to get the most recent interaction
        runs = sorted(runs, key=lambda run: run.start_time, reverse=True)

        # Get the most recent run
        latest_run = runs[0]

        # Extract messages from inputs and outputs
        messages = []

        # Add input messages if they exist
        if hasattr(latest_run, "inputs") and "messages" in latest_run.inputs:
            messages.extend(latest_run.inputs["messages"])

        # Add output message if it exists
        if hasattr(latest_run, "outputs"):
            if isinstance(latest_run.outputs, dict) and "choices" in latest_run.outputs:
                if (
                    isinstance(latest_run.outputs["choices"], list)
                    and len(latest_run.outputs["choices"]) > 0
                ):
                    if "message" in latest_run.outputs["choices"][0]:
                        messages.append(latest_run.outputs["choices"][0]["message"])
            elif isinstance(latest_run.outputs, dict) and "message" in latest_run.outputs:
                messages.append(latest_run.outputs["message"])

        if not messages or len(messages) == 0:
            return {"error": f"No messages found in the run for thread {thread_id}"}

        return {"result": messages}

    except Exception as e:
        return {"error": f"Error fetching thread history: {str(e)}"}


def fetch_run_tool(client, run_id: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific run by its run ID.
    
    This function provides comprehensive analysis of a single run, including:
    - Run metadata (type, status, timing, costs)
    - Input and output data
    - Error information if applicable
    - Child runs (sub-steps) that are part of this run
    
    Args:
        client: LangSmith client instance
        run_id: The ID of the run to fetch
    
    Returns:
        Dictionary containing detailed run information and child runs
    """
    # Handle None values and "null" string inputs
    if run_id == "null" or not run_id:
        return {"error": "Error: run_id must be provided."}
    
    try:
        # Get the specific run
        run = client.read_run(run_id)
        
        if not run:
            return {"error": f"No run found with ID: {run_id}"}
        
        # Build the main run information
        run_info = {
            "id": str(run.id),
            "name": run.name,
            "run_type": run.run_type,
            "status": run.status if hasattr(run, "status") else None,
            "start_time": str(run.start_time) if hasattr(run, "start_time") else None,
            "end_time": str(run.end_time) if hasattr(run, "end_time") else None,
            "latency_ms": run.latency if hasattr(run, "latency") else None,
            "inputs": run.inputs,
            "outputs": run.outputs,
            "error": run.error,
            "total_tokens": run.total_tokens if hasattr(run, "total_tokens") else None,
            "prompt_tokens": run.prompt_tokens if hasattr(run, "prompt_tokens") else None,
            "completion_tokens": run.completion_tokens if hasattr(run, "completion_tokens") else None,
            "total_cost": str(run.total_cost) if hasattr(run, "total_cost") else None,
            "prompt_cost": str(run.prompt_cost) if hasattr(run, "prompt_cost") else None,
            "completion_cost": str(run.completion_cost) if hasattr(run, "completion_cost") else None,
            "tags": run.tags if hasattr(run, "tags") else [],
            "trace_id": str(run.trace_id) if hasattr(run, "trace_id") else None,
            "parent_run_id": str(run.parent_run_id) if hasattr(run, "parent_run_id") and run.parent_run_id else None,
        }
        
        # Get child runs to understand the full execution tree
        child_runs = []
        try:
            children = list(client.list_runs(
                trace_id=str(run.trace_id) if hasattr(run, "trace_id") else None,
                select=[
                    "id",
                    "name", 
                    "run_type",
                    "status",
                    "start_time",
                    "end_time",
                    "latency",
                    "error",
                    "parent_run_id",
                    "inputs",
                    "outputs",
                    "total_tokens",
                    "total_cost",
                ],
            ))
            
            # Filter to only include direct children and order them
            child_runs = [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "run_type": c.run_type,
                    "status": c.status if hasattr(c, "status") else None,
                    "start_time": str(c.start_time) if hasattr(c, "start_time") else None,
                    "end_time": str(c.end_time) if hasattr(c, "end_time") else None,
                    "latency_ms": c.latency if hasattr(c, "latency") else None,
                    "error": c.error,
                    "inputs": c.inputs,
                    "outputs": c.outputs,
                    "total_tokens": c.total_tokens if hasattr(c, "total_tokens") else None,
                    "total_cost": str(c.total_cost) if hasattr(c, "total_cost") else None,
                }
                for c in children
                if hasattr(c, "parent_run_id") and c.parent_run_id and str(c.parent_run_id) == run_id
            ]
            
            # Sort by start time
            child_runs.sort(key=lambda x: x.get("start_time", ""))
            
        except Exception as e:
            # If we can't get child runs, that's okay - just note it
            run_info["child_runs_error"] = f"Could not fetch child runs: {str(e)}"
        
        run_info["child_runs"] = child_runs
        run_info["child_run_count"] = len(child_runs)
        
        return run_info
        
    except Exception as e:
        return {"error": f"Error fetching run: {str(e)}"}


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
