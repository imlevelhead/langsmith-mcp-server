"""
Client for interacting with the LangSmith API.
Provides low-level API operations that can be used by higher-level tools.
"""

import os
from typing import Optional

from langsmith import Client


class LangSmithClient:
    """Client for interacting with the LangSmith API."""

    def __init__(
        self, 
        api_key: str, 
        workspace_id: Optional[str] = None, 
        endpoint: Optional[str] = None
    ):
        """
        Initialize the LangSmith API client.

        Args:
            api_key: API key for LangSmith API (required)
            workspace_id: Optional workspace ID for API keys scoped to multiple workspaces
            endpoint: Optional custom endpoint URL (e.g., for self-hosted installations or EU region)
        """
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.endpoint = endpoint
        
        # Set environment variables for LangSmith client
        os.environ["LANGSMITH_API_KEY"] = api_key
        if workspace_id:
            os.environ["LANGSMITH_WORKSPACE_ID"] = workspace_id
        if endpoint:
            os.environ["LANGSMITH_ENDPOINT"] = endpoint
        
        # Initialize the LangSmith client with optional parameters
        client_kwargs = {"api_key": api_key}
        if workspace_id:
            client_kwargs["workspace_id"] = workspace_id
        if endpoint:
            client_kwargs["api_url"] = endpoint
            
        self.langsmith_client = Client(**client_kwargs)

    def get_client(self) -> Client:
        """Get the underlying LangSmith client."""
        return self.langsmith_client
