#!/usr/bin/env python3
"""
Execute Step 12 of AIRAS workflow: Citation Subgraph
Following the MANDATORY 3-step cycle:
1. Download state from GitHub
2. Execute citation_subgraph
3. Upload updated state to GitHub
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path to import airas modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.airas.features.write.citation_subgraph.citation_subgraph import CitationSubgraph
from src.airas.features.github.nodes.github_download import github_download
from src.airas.features.github.nodes.github_upload import github_upload

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Execute Step 12: Citation Subgraph with 3-step cycle"""
    
    # Configuration
    github_repository = "auto-res2/test-kumagai-20250731-v2"
    branch_name = "test"
    llm_name = "o3-mini-2025-01-31"
    
    logger.info("=== STEP 12: CITATION SUBGRAPH ===")
    
    # Step 12.1: Download State
    logger.info("\n--- Step 12.1: Download State ---")
    logger.info(f"Downloading state from GitHub repository: {github_repository}, branch: {branch_name}")
    
    try:
        download_result = github_download(
            github_repository=github_repository,
            branch_name=branch_name
        )
        state = download_result["state"]
        logger.info("Successfully downloaded state from GitHub")
        logger.info(f"State keys: {list(state.keys())}")
    except Exception as e:
        logger.error(f"Failed to download state: {e}")
        raise
    
    # Step 12.2: Execute Citation Subgraph
    logger.info("\n--- Step 12.2: Execute Citation Subgraph ---")
    
    # Prepare input for citation subgraph
    if "paper_content" not in state:
        logger.error("paper_content not found in state!")
        # Try to load from paper_content.json file
        paper_content_path = Path(__file__).parent / "paper_content.json"
        if paper_content_path.exists():
            with open(paper_content_path, 'r') as f:
                paper_content = json.load(f)
            logger.info("Loaded paper_content from file")
        else:
            raise ValueError("paper_content not found in state or file!")
    else:
        paper_content = state["paper_content"]
    
    # Prepare input for citation subgraph
    citation_input = {
        "paper_content": paper_content
    }
    
    logger.info("Executing citation subgraph...")
    logger.info(f"Paper sections: {list(paper_content.keys())}")
    
    try:
        # Create and run citation subgraph
        citation_subgraph = CitationSubgraph(llm_name=llm_name)
        citation_result = citation_subgraph.run(citation_input)
        
        logger.info("Citation subgraph completed successfully")
        logger.info(f"Result keys: {list(citation_result.keys())}")
        
        # Update state with citation results
        state["paper_content_with_placeholders"] = citation_result["paper_content_with_placeholders"]
        state["references"] = citation_result["references"]
        state["citation_step_completed"] = True
        
        # Log some details about the results
        logger.info(f"Number of references found: {len(citation_result.get('references', {}))}")
        
    except Exception as e:
        logger.error(f"Failed to execute citation subgraph: {e}")
        raise
    
    # Step 12.3: Upload State
    logger.info("\n--- Step 12.3: Upload State ---")
    logger.info("Uploading updated state back to GitHub...")
    
    try:
        upload_result = github_upload(
            state=state,
            github_repository=github_repository,
            branch_name=branch_name,
            subgraph_name="citation_subgraph"
        )
        logger.info("Successfully uploaded state to GitHub")
        logger.info(f"Upload result: {upload_result}")
    except Exception as e:
        logger.error(f"Failed to upload state: {e}")
        raise
    
    # Save state locally as backup
    output_path = Path(__file__).parent / "state_step12_complete.json"
    with open(output_path, 'w') as f:
        json.dump(state, f, indent=2)
    logger.info(f"State saved locally to: {output_path}")
    
    # Save paper with citations locally
    paper_with_citations_path = Path(__file__).parent / "paper_with_citations.json"
    with open(paper_with_citations_path, 'w') as f:
        json.dump({
            "paper_content_with_placeholders": citation_result["paper_content_with_placeholders"],
            "references": citation_result["references"]
        }, f, indent=2)
    logger.info(f"Paper with citations saved to: {paper_with_citations_path}")
    
    logger.info("\n=== STEP 12 COMPLETED SUCCESSFULLY ===")
    logger.info("Citation placeholders have been embedded and references generated.")
    logger.info("The paper is now ready for LaTeX compilation in Step 13.")

if __name__ == "__main__":
    main()