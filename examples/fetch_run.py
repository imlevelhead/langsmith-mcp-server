"""
Example: Fetch a specific run by its run ID

This example demonstrates how to use the fetch_run tool to get detailed
information about a specific run, including its child runs.

A trace can contain multiple runs. This tool is useful when you:
- Have a specific run ID and want to understand what happened in that execution
- Need to debug a particular step in a larger trace
- Want to analyze the child runs (sub-steps) of a specific run
- Need detailed timing, cost, and error information for a run
"""

from langsmith import Client

# Initialize the LangSmith client
client = Client()

# Replace with your actual run ID
run_id = "your-run-id-here"

# Fetch the run details
try:
    # Using the client directly (this simulates what the MCP tool does internally)
    run = client.read_run(run_id)
    
    print(f"Run ID: {run.id}")
    print(f"Run Name: {run.name}")
    print(f"Run Type: {run.run_type}")
    print(f"Status: {run.status if hasattr(run, 'status') else 'N/A'}")
    print(f"Start Time: {run.start_time if hasattr(run, 'start_time') else 'N/A'}")
    print(f"End Time: {run.end_time if hasattr(run, 'end_time') else 'N/A'}")
    print(f"Latency (ms): {run.latency if hasattr(run, 'latency') else 'N/A'}")
    print(f"Total Tokens: {run.total_tokens if hasattr(run, 'total_tokens') else 'N/A'}")
    print(f"Total Cost: {run.total_cost if hasattr(run, 'total_cost') else 'N/A'}")
    print(f"Error: {run.error if run.error else 'None'}")
    
    print("\n--- Inputs ---")
    print(run.inputs)
    
    print("\n--- Outputs ---")
    print(run.outputs)
    
    # Get child runs
    print("\n--- Child Runs ---")
    trace_id = run.trace_id if hasattr(run, "trace_id") else None
    if trace_id:
        children = list(client.list_runs(trace_id=str(trace_id)))
        child_runs = [
            c for c in children
            if hasattr(c, "parent_run_id") and c.parent_run_id and str(c.parent_run_id) == str(run_id)
        ]
        
        print(f"Found {len(child_runs)} child runs:")
        for i, child in enumerate(child_runs, 1):
            print(f"\n  {i}. {child.name} ({child.run_type})")
            print(f"     ID: {child.id}")
            print(f"     Status: {child.status if hasattr(child, 'status') else 'N/A'}")
            print(f"     Latency: {child.latency if hasattr(child, 'latency') else 'N/A'} ms")
            if child.error:
                print(f"     Error: {child.error}")
    else:
        print("No trace ID available to fetch child runs")
    
except Exception as e:
    print(f"Error fetching run: {e}")


print("\n" + "="*60)
print("To use this via the MCP server:")
print("="*60)
print("""
1. Call the 'fetch_run' tool with your run_id:
   - run_id: The ID of the run you want to analyze

2. The tool will return:
   - Complete run metadata (name, type, status, timing)
   - Input and output data
   - Token usage and cost information
   - Error information if the run failed
   - List of all child runs (sub-steps) with their details
   - Parent run ID if this run is part of a larger execution
   - Trace ID for additional context

3. Use cases:
   - Debug a specific failing step in a multi-step trace
   - Analyze token usage and costs for a particular LLM call
   - Understand the execution tree by examining child runs
   - Compare inputs vs outputs for a specific operation
   - Track error propagation through nested runs
""")

