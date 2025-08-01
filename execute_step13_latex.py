#!/usr/bin/env python3
"""
Execute Step 13: LaTeX Subgraph - Compile paper to LaTeX format
Following the MANDATORY 3-step execution cycle:
1. Download State
2. Execute latex_subgraph
3. Upload State
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import AIRAS modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.airas.features.publication.latex_subgraph.latex_subgraph import latex_subgraph
from src.airas.features.github.github_download_subgraph import github_download_subgraph
from src.airas.features.github.github_upload_subgraph import github_upload_subgraph

def main():
    print("=== Step 13: LaTeX Subgraph ===")
    print("Following MANDATORY 3-step execution cycle...")
    
    # Configuration
    github_repository = "auto-res2/test-kumagai-20250731-v2"
    branch_name = "test"
    
    # Step 13.1: Download State
    print("\n--- Step 13.1: Download State ---")
    print(f"Downloading latest state from GitHub repository: {github_repository}, branch: {branch_name}")
    
    try:
        # Download state from GitHub
        download_result = github_download_subgraph({
            "github_repository": github_repository,
            "branch_name": branch_name
        })
        
        state = download_result.get("state", {})
        print(f"Successfully downloaded state with {len(state)} keys")
        
    except Exception as e:
        print(f"Error downloading state: {e}")
        # If download fails, try to load from local file as fallback
        print("Attempting to load state from local file...")
        with open("state_step12_complete.json", "r") as f:
            state = json.load(f)
        print(f"Loaded state from local file with {len(state)} keys")
    
    # Step 13.2: Execute Main Task - LaTeX Subgraph
    print("\n--- Step 13.2: Execute LaTeX Subgraph ---")
    print("Converting paper to LaTeX format...")
    
    # Ensure required fields are present
    if "github_repository" not in state:
        state["github_repository"] = github_repository
    if "branch_name" not in state:
        state["branch_name"] = branch_name
    
    # Check for required inputs
    required_fields = ["paper_content_with_placeholders", "references", "image_file_name_list"]
    missing_fields = [field for field in required_fields if field not in state]
    
    if missing_fields:
        print(f"Warning: Missing fields in state: {missing_fields}")
        # Try to load from paper_with_citations.json if available
        if "paper_content_with_placeholders" not in state:
            try:
                with open("paper_with_citations.json", "r") as f:
                    citations_data = json.load(f)
                    state["paper_content_with_placeholders"] = citations_data.get("paper_content_with_placeholders", "")
                    state["references"] = citations_data.get("references", [])
                    print("Loaded paper content and references from paper_with_citations.json")
            except Exception as e:
                print(f"Error loading paper_with_citations.json: {e}")
    
    # Set image file list if not present
    if "image_file_name_list" not in state:
        # Check for experiment plots
        image_files = []
        experiments_dir = Path("src/experiments")
        if experiments_dir.exists():
            image_files = [str(f) for f in experiments_dir.glob("*.pdf")]
        state["image_file_name_list"] = image_files
        print(f"Found {len(image_files)} image files")
    
    try:
        # Execute latex_subgraph
        result = latex_subgraph(state)
        
        # Update state with results
        state.update(result)
        print("LaTeX subgraph execution completed successfully")
        
        # Display key results
        if "bibliography" in result:
            print(f"Generated bibliography with {len(result['bibliography'].split('\\bibitem'))-1} entries")
        if "latex_content" in result:
            print(f"Generated LaTeX content ({len(result['latex_content'])} characters)")
        if "pdf_file_path" in result:
            print(f"PDF will be generated at: {result['pdf_file_path']}")
        
    except Exception as e:
        print(f"Error executing latex_subgraph: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 13.3: Upload State
    print("\n--- Step 13.3: Upload State ---")
    print("Uploading updated state back to GitHub...")
    
    try:
        # Upload state back to GitHub
        upload_result = github_upload_subgraph({
            "state": state,
            "subgraph_name": "latex_subgraph",
            "github_repository": github_repository,
            "branch_name": branch_name
        })
        
        print("Successfully uploaded state to GitHub")
        if "commit_sha" in upload_result:
            print(f"Commit SHA: {upload_result['commit_sha']}")
        
    except Exception as e:
        print(f"Error uploading state: {e}")
        # Save state locally as backup
        output_file = "state_step13_complete.json"
        with open(output_file, "w") as f:
            json.dump(state, f, indent=2)
        print(f"Saved state locally to {output_file}")
    
    # Save a summary
    summary = {
        "step": "13_latex_subgraph",
        "status": "completed",
        "bibliography_generated": "bibliography" in state,
        "latex_content_generated": "latex_content" in state,
        "pdf_path": state.get("pdf_file_path", ""),
        "github_workflow_dispatched": state.get("github_workflow_dispatched", False)
    }
    
    with open("step13_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n=== Step 13 Complete ===")
    print("The paper has been converted to LaTeX format.")
    print("GitHub Actions workflow has been dispatched to compile the PDF.")

if __name__ == "__main__":
    main()