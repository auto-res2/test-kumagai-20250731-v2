#!/usr/bin/env python3
"""Test AIRAS prepare_repository_subgraph with updated credentials."""

import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the AIRAS source directory to Python path
sys.path.insert(0, '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/src')

from airas.features.github.prepare_repository_subgraph.prepare_repository_subgraph import PrepareRepositorySubgraph

# Create initial state
initial_state = {
    "query": "Self-attention mechanisms for efficient transformers",
    "github_repository": "auto-res2/test-kumagai-20250801-v1",  # Changed from repo_path
    "branch_name": "test-v2",
    "base_paper": None,
    "related_papers": [],
    "code_snippets": [],
    "method": None,
    "experimental_design": None,
    "generated_code": None,
    "executed_code": None,
    "executed_flag": False,
    "analytic_result": None,
    "paper_draft": None,
    "citations": None,
    "latex_output": None,
    "html_output": None,
    "readme_content": None,
    "errors": [],
    "timestamp": datetime.now().isoformat()
}

print("Initial state created:")
print(json.dumps(initial_state, indent=2))

print("\nPreparing to execute prepare_repository_subgraph...")
print(f"Repository: {initial_state['github_repository']}")
print(f"Branch: {initial_state['branch_name']}")
print(f"Query: {initial_state['query']}")

# Initialize and execute the subgraph
try:
    subgraph = PrepareRepositorySubgraph()
    result = subgraph.run(initial_state)  # Using run() method as shown in MCP server
    
    print("\n✅ Success! Repository prepared successfully.")
    print("\nUpdated state:")
    print(json.dumps(result, indent=2))
    
    # Save the state
    with open('test_prepare_state.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\nState saved to test_prepare_state.json")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()