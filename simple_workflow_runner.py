#!/usr/bin/env python3
"""
Simplified AIRAS workflow runner - focus on core functionality
"""
import sys
import os
import json
from datetime import datetime

# Add the airas source directory to the Python path
sys.path.insert(0, "/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1")

# Import required modules
from airas.features.retrieve.retrieve_paper_from_query_subgraph.retrieve_paper_from_query_subgraph import RetrievePaperFromQuerySubgraph

def main():
    """Run a simplified version focusing on arxiv papers"""
    
    # Initialize state
    state = {
        "github_repository": "auto-res2/test-kumagai-20250731-v2",
        "branch_name": "test-2",
        "base_queries": ["Quantum-inspired algorithms for neural network optimization"],
        "subgraph_name": "quantum_airas_workflow"
    }
    
    print("Starting simplified AIRAS workflow...")
    print(f"Query: {state['base_queries'][0]}")
    print(f"Repository: {state['github_repository']}")
    print(f"Branch: {state['branch_name']}")
    
    try:
        # Skip web scraping and focus on arxiv search
        print("\nStep 2: Searching for papers on quantum-inspired algorithms...")
        
        # Create a modified version that skips ICML scraping
        subgraph = RetrievePaperFromQuerySubgraph(
            llm_name="gemini-2.0-flash-001",
            save_dir="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/data",
            scrape_urls=[]  # Empty list to skip web scraping
        )
        
        # Run the subgraph
        state = subgraph.run(state)
        
        # Save the state
        with open("quantum_workflow_state.json", 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        print("\nWorkflow completed!")
        print(f"State saved to: quantum_workflow_state.json")
        
        if "base_method_text" in state:
            print(f"\nBase paper found:")
            print(f"  Title: {state['base_method_text'].get('title', 'Unknown')}")
            print(f"  ArXiv URL: {state['base_method_text'].get('arxiv_url', 'Unknown')}")
        
        if "base_github_url" in state:
            print(f"  GitHub URL: {state['base_github_url']}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Save error state
        state["error"] = str(e)
        with open("quantum_workflow_error.json", 'w') as f:
            json.dump(state, f, indent=2, default=str)

if __name__ == "__main__":
    main()