#!/usr/bin/env python3
"""
Continue AIRAS workflow from Step 2
"""
import sys
import os
import json
import traceback
from datetime import datetime

# Add the airas source directory to the Python path
sys.path.insert(0, "/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1")

# Import required subgraphs
from airas.features.retrieve.retrieve_paper_from_query_subgraph.retrieve_paper_from_query_subgraph import RetrievePaperFromQuerySubgraph
from airas.features.github.github_download_subgraph import GithubDownloadSubgraph
from airas.features.github.github_upload_subgraph import GithubUploadSubgraph

def log_step(step_num, description, state=None):
    """Log workflow step progress"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*80}")
    print(f"[{timestamp}] Step {step_num}: {description}")
    print(f"{'='*80}")
    if state:
        print(f"Current state keys: {list(state.keys())}")

def save_state(state, filename="workflow_state.json"):
    """Save state to file"""
    with open(filename, 'w') as f:
        json.dump(state, f, indent=2, default=str)
    print(f"State saved to {filename}")

def main():
    """Continue from Step 2"""
    
    # Load state from step 1
    try:
        with open("state_step1_prepare.json", 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        # Initialize state if file not found
        state = {
            "github_repository": "auto-res2/test-kumagai-20250731-v2",
            "branch_name": "test-2",
            "base_queries": ["Quantum-inspired algorithms for neural network optimization"],
            "subgraph_name": "quantum_airas_workflow"
        }
    
    try:
        # Step 2: Retrieve paper from query (with 3-step cycle)
        log_step(2.1, "Download state before retrieve_paper_from_query", state)
        try:
            state = GithubDownloadSubgraph().run(state)
        except Exception as e:
            print(f"Warning: GitHub download failed: {e}")
            print("Continuing with current state...")
        
        log_step(2.2, "Execute retrieve_paper_from_query_subgraph", state)
        state = RetrievePaperFromQuerySubgraph(
            llm_name="gemini-2.0-flash-001",  # Using available model
            save_dir="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/data",
            scrape_urls=["https://icml.cc/virtual/2024/papers.html?filter=title"]
        ).run(state)
        
        log_step(2.3, "Upload state after retrieve_paper_from_query", state)
        try:
            state = GithubUploadSubgraph().run(state)
        except Exception as e:
            print(f"Warning: GitHub upload failed: {e}")
            print("Continuing...")
        
        save_state(state, "state_step2_retrieve_paper.json")
        
        # Final summary
        print(f"\n{'='*80}")
        print("Step 2 COMPLETED!")
        print(f"{'='*80}")
        
        if "base_method_text" in state:
            print(f"\nBase paper found: {state['base_method_text'].get('title', 'Unknown')}")
        
        if "base_github_url" in state:
            print(f"GitHub URL: {state['base_github_url']}")
        
        print(f"\nState saved to: state_step2_retrieve_paper.json")
        print("\nNext: Run continue_workflow_step3.py to proceed with related paper retrieval")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"ERROR: Step 2 failed")
        print(f"Error details: {str(e)}")
        print(f"{'='*80}")
        traceback.print_exc()
        save_state(state, "state_step2_error.json")
        raise

if __name__ == "__main__":
    main()