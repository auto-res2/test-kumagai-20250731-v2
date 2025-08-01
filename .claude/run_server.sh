#!/bin/bash

# Set PYTHONPATH to include the airas source directory
export PYTHONPATH="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1:$PYTHONPATH"

# Change to the airas directory
cd /Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1

# Run the MCP server
exec uv run fastmcp run src/airas/services/mcp_server/mcp_server.py