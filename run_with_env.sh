#!/bin/bash

# Load environment variables from .env file
set -a
source /Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/.env
set +a

# Set PYTHONPATH
export PYTHONPATH="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1:$PYTHONPATH"

# Change to the airas directory
cd /Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1

# Run the command passed as argument
exec uv run "$@"