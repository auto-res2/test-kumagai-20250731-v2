#!/usr/bin/env python3
"""
Execute the complete AIRAS workflow for quantum-inspired algorithms research
"""
import sys
import os
import json
from datetime import datetime

# Add the airas source directory to the Python path
sys.path.insert(0, "/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1")

# Import all the necessary subgraphs
from airas.features.github.prepare_repository_subgraph.prepare_repository_subgraph import PrepareRepositorySubgraph
from airas.features.retrieve.retrieve_paper_from_query_subgraph.retrieve_paper_from_query_subgraph import RetrievePaperFromQuerySubgraph
from airas.features.retrieve.retrieve_related_paper_subgraph.retrieve_related_paper_subgraph import RetrieveRelatedPaperSubgraph
from airas.features.retrieve.retrieve_code_subgraph.retrieve_code_subgraph import RetrieveCodeSubgraph
from airas.features.create.create_method_subgraph.create_method_subgraph import CreateMethodSubgraph
from airas.features.create.create_experimental_design_subgraph.create_experimental_design_subgraph import CreateExperimentalDesignSubgraph
from airas.features.create.create_code_subgraph.create_code_subgraph import CreateCodeSubgraph
from airas.features.execution.github_actions_executor_subgraph.github_actions_executor_subgraph import GitHubActionsExecutorSubgraph
from airas.features.create.fix_code_subgraph.fix_code_subgraph import FixCodeSubgraph
from airas.features.analysis.analytic_subgraph.analytic_subgraph import AnalyticSubgraph
from airas.features.write.writer_subgraph.writer_subgraph import WriterSubgraph
from airas.features.write.citation_subgraph.citation_subgraph import CitationSubgraph
from airas.features.publication.readme_subgraph.readme_subgraph import ReadmeSubgraph
from airas.features.publication.html_subgraph.html_subgraph import HtmlSubgraph
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
        json.dump(state, f, indent=2)
    print(f"State saved to {filename}")

def main():
    """Execute the complete AIRAS workflow"""
    
    # Initialize state
    state = {
        "github_repository": "auto-res2/test-kumagai-20250731-v2",
        "branch_name": "test-2",
        "base_queries": ["Quantum-inspired algorithms for neural network optimization"],
        "subgraph_name": "quantum_airas_workflow"
    }
    
    try:
        # Step 1: Prepare repository
        log_step(1, "Prepare repository using prepare_repository_subgraph", state)
        state = PrepareRepositorySubgraph().run(state)
        save_state(state, "state_step1_prepare.json")
        
        # Step 2: Retrieve paper from query (with 3-step cycle)
        log_step(2.1, "Download state before retrieve_paper_from_query", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(2.2, "Execute retrieve_paper_from_query_subgraph", state)
        state = RetrievePaperFromQuerySubgraph(
            llm_name="o3-mini-2025-01-31",
            save_dir="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/data",
            scrape_urls=["https://icml.cc/virtual/2024/papers.html?filter=title"]
        ).run(state)
        
        log_step(2.3, "Upload state after retrieve_paper_from_query", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step2_retrieve_paper.json")
        
        # Step 3: Retrieve related papers (with 3-step cycle)
        log_step(3.1, "Download state before retrieve_related_paper", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(3.2, "Execute retrieve_related_paper_subgraph", state)
        state = RetrieveRelatedPaperSubgraph(
            llm_name="o3-mini-2025-01-31",
            save_dir="/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/data",
            scrape_urls=["https://icml.cc/virtual/2024/papers.html?filter=title"],
            add_paper_num=1
        ).run(state)
        
        log_step(3.3, "Upload state after retrieve_related_paper", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step3_related_papers.json")
        
        # Step 4: Retrieve code (with 3-step cycle)
        log_step(4.1, "Download state before retrieve_code", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(4.2, "Execute retrieve_code_subgraph", state)
        state = RetrieveCodeSubgraph().run(state)
        
        log_step(4.3, "Upload state after retrieve_code", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step4_retrieve_code.json")
        
        # Step 5: Create method (with 3-step cycle)
        log_step(5.1, "Download state before create_method", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(5.2, "Execute create_method_subgraph", state)
        state = CreateMethodSubgraph(llm_name="o3-mini-2025-01-31").run(state)
        
        log_step(5.3, "Upload state after create_method", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step5_create_method.json")
        
        # Step 6: Create experimental design (with 3-step cycle)
        log_step(6.1, "Download state before create_experimental_design", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(6.2, "Execute create_experimental_design_subgraph", state)
        state = CreateExperimentalDesignSubgraph().run(state)
        
        log_step(6.3, "Upload state after create_experimental_design", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step6_experimental_design.json")
        
        # Step 7: Create code (with 3-step cycle)
        log_step(7.1, "Download state before create_code", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(7.2, "Execute create_code_subgraph", state)
        state = CreateCodeSubgraph().run(state)
        
        log_step(7.3, "Upload state after create_code", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step7_create_code.json")
        
        # Step 8: Execute GitHub Actions (with 3-step cycle)
        log_step(8.1, "Download state before github_actions_executor", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(8.2, "Execute github_actions_executor_subgraph", state)
        state = GitHubActionsExecutorSubgraph(gpu_enabled=False).run(state)
        
        log_step(8.3, "Upload state after github_actions_executor", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step8_github_actions.json")
        
        # Step 9: Fix code if needed (loop until executed_flag is true)
        iteration = 0
        while not state.get("executed_flag", False) and iteration < 5:
            iteration += 1
            log_step(f"9.{iteration}.1", f"Download state before fix_code (iteration {iteration})", state)
            state = GithubDownloadSubgraph().run(state)
            
            log_step(f"9.{iteration}.2", f"Execute fix_code_subgraph (iteration {iteration})", state)
            state = FixCodeSubgraph().run(state)
            
            log_step(f"9.{iteration}.3", f"Upload state after fix_code (iteration {iteration})", state)
            state = GithubUploadSubgraph().run(state)
            
            # Re-run GitHub Actions
            log_step(f"9.{iteration}.4", f"Download state before re-run github_actions (iteration {iteration})", state)
            state = GithubDownloadSubgraph().run(state)
            
            log_step(f"9.{iteration}.5", f"Re-execute github_actions_executor_subgraph (iteration {iteration})", state)
            state = GitHubActionsExecutorSubgraph(gpu_enabled=False).run(state)
            
            log_step(f"9.{iteration}.6", f"Upload state after re-run github_actions (iteration {iteration})", state)
            state = GithubUploadSubgraph().run(state)
            save_state(state, f"state_step9_fix_iteration_{iteration}.json")
        
        # Step 10: Analyze results (with 3-step cycle)
        log_step(10.1, "Download state before analytic", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(10.2, "Execute analytic_subgraph", state)
        state = AnalyticSubgraph(llm_name="o3-mini-2025-01-31").run(state)
        
        log_step(10.3, "Upload state after analytic", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step10_analytic.json")
        
        # Step 11: Write paper (with 3-step cycle)
        log_step(11.1, "Download state before writer", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(11.2, "Execute writer_subgraph", state)
        state = WriterSubgraph(llm_name="o3-mini-2025-01-31", refine_round=1).run(state)
        
        log_step(11.3, "Upload state after writer", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step11_writer.json")
        
        # Step 12: Generate citations (with 3-step cycle)
        log_step(12.1, "Download state before citation", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(12.2, "Execute citation_subgraph", state)
        state = CitationSubgraph(llm_name="o3-mini-2025-01-31").run(state)
        
        log_step(12.3, "Upload state after citation", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step12_citation.json")
        
        # Step 13: Create README (with 3-step cycle)
        log_step(13.1, "Download state before readme", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(13.2, "Execute readme_subgraph", state)
        state = ReadmeSubgraph().run(state)
        
        log_step(13.3, "Upload state after readme", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step13_readme.json")
        
        # Step 14: Generate HTML (with 3-step cycle)
        log_step(14.1, "Download state before html", state)
        state = GithubDownloadSubgraph().run(state)
        
        log_step(14.2, "Execute html_subgraph", state)
        state = HtmlSubgraph(llm_name="o3-mini-2025-01-31").run(state)
        
        log_step(14.3, "Upload state after html", state)
        state = GithubUploadSubgraph().run(state)
        save_state(state, "state_step14_html.json")
        
        # Final summary
        print(f"\n{'='*80}")
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        
        if "github_pages_url" in state:
            print(f"\nFinal HTML URL: {state['github_pages_url']}")
        
        print(f"\nFinal state saved to: state_step14_html.json")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"ERROR: Workflow failed at step")
        print(f"Error details: {str(e)}")
        print(f"{'='*80}")
        save_state(state, "state_error.json")
        raise

if __name__ == "__main__":
    main()