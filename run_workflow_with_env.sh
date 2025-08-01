#!/bin/bash

# Change to the airas directory
cd /Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set PYTHONPATH
export PYTHONPATH="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1:$PYTHONPATH"

# Change back to the working directory
cd /Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/temp_repo/test-kumagai-20250731-v2

# Run the workflow using uv
uv run python run_quantum_airas_workflow.py