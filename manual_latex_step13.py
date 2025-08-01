#!/usr/bin/env python3
"""
Manual execution of Step 13: LaTeX Subgraph
This version works directly with local files without GitHub integration
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import AIRAS modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.airas.features.publication.latex_subgraph.nodes.generate_bib import generate_bib
from src.airas.features.publication.latex_subgraph.nodes.convert_to_latex import convert_to_latex
from src.airas.features.publication.latex_subgraph.nodes.assemble_latex import assemble_latex

def main():
    print("=== Manual Step 13: LaTeX Conversion ===")
    
    # Step 1: Load state from local file
    print("\n--- Loading State ---")
    try:
        with open("state_step12_complete.json", "r") as f:
            state = json.load(f)
        print(f"Loaded state with {len(state)} keys")
    except FileNotFoundError:
        print("state_step12_complete.json not found, creating minimal state...")
        state = {}
    
    # Load paper content if not in state
    if "paper_content_with_placeholders" not in state:
        try:
            with open("paper_with_citations.json", "r") as f:
                citations_data = json.load(f)
                state["paper_content_with_placeholders"] = citations_data.get("paper_content_with_placeholders", "")
                state["references"] = citations_data.get("references", [])
                print("Loaded paper content from paper_with_citations.json")
        except Exception as e:
            print(f"Error loading paper_with_citations.json: {e}")
            # Try loading from markdown file
            try:
                with open("paper_with_citations.md", "r") as f:
                    state["paper_content_with_placeholders"] = f.read()
                print("Loaded paper content from paper_with_citations.md")
            except Exception as e:
                print(f"Error loading paper_with_citations.md: {e}")
                return
    
    # Set default values
    state["github_repository"] = state.get("github_repository", "auto-res2/test-kumagai-20250731-v2")
    state["branch_name"] = state.get("branch_name", "test")
    
    # Find image files
    image_files = []
    experiments_dir = Path("src/experiments")
    if experiments_dir.exists():
        image_files = [str(f.relative_to(Path.cwd())) for f in experiments_dir.glob("*.pdf")]
    state["image_file_name_list"] = image_files
    print(f"Found {len(image_files)} image files: {image_files}")
    
    # Step 2: Generate Bibliography
    print("\n--- Generating Bibliography ---")
    try:
        bib_result = generate_bib(state)
        state.update(bib_result)
        print(f"Generated bibliography with {len(bib_result.get('bibliography', '').split('\\\\bibitem'))-1} entries")
    except Exception as e:
        print(f"Error generating bibliography: {e}")
        state["bibliography"] = ""  # Empty bibliography as fallback
    
    # Step 3: Convert to LaTeX
    print("\n--- Converting to LaTeX ---")
    try:
        latex_result = convert_to_latex(state)
        state.update(latex_result)
        print(f"Generated LaTeX content ({len(latex_result.get('latex_content', ''))} characters)")
    except Exception as e:
        print(f"Error converting to LaTeX: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Assemble LaTeX Document
    print("\n--- Assembling LaTeX Document ---")
    try:
        assemble_result = assemble_latex(state)
        state.update(assemble_result)
        print("LaTeX document assembled successfully")
        
        # Save the LaTeX files
        if "latex_files" in assemble_result:
            os.makedirs("latex_output", exist_ok=True)
            for filename, content in assemble_result["latex_files"].items():
                output_path = Path("latex_output") / filename
                with open(output_path, "w") as f:
                    f.write(content)
                print(f"Saved: {output_path}")
        
    except Exception as e:
        print(f"Error assembling LaTeX: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Save updated state
    print("\n--- Saving State ---")
    with open("state_step13_complete.json", "w") as f:
        json.dump(state, f, indent=2)
    print("Saved state to state_step13_complete.json")
    
    # Create summary
    summary = {
        "step": "13_latex_subgraph",
        "status": "completed",
        "bibliography_generated": bool(state.get("bibliography")),
        "latex_content_generated": bool(state.get("latex_content")),
        "latex_files_created": list(state.get("latex_files", {}).keys()) if "latex_files" in state else [],
        "image_files": state.get("image_file_name_list", [])
    }
    
    with open("step13_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n=== Manual Step 13 Complete ===")
    print("LaTeX files have been generated in the 'latex_output' directory.")
    print("To compile the PDF, run: pdflatex -output-directory=latex_output latex_output/main.tex")

if __name__ == "__main__":
    main()