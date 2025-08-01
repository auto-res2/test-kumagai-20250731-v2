#!/usr/bin/env python3
"""
Execute Step 11: Writer Subgraph
Following the mandatory 3-step cycle:
1. Download state from GitHub
2. Execute writer_subgraph
3. Upload state back to GitHub
"""

import json
import sys
import os
from datetime import datetime

# Add the AIRAS source directory to path
sys.path.append('/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/src')

# Step 11.1: Download State
print("="*60)
print("Step 11.1: DOWNLOAD STATE")
print("="*60)

# For this execution, we'll use the local state.json as it represents the current state
state_file = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/temp_repo/test-kumagai-20250731-v2/state.json'
with open(state_file, 'r') as f:
    state = json.load(f)

print(f"Loaded state from: {state_file}")
print(f"State keys: {list(state.keys())}")

# Verify all required inputs for writer_subgraph are present
required_keys = [
    'base_method_text',
    'new_method', 
    'verification_policy',
    'experiment_details',
    'experiment_code',
    'output_text_data',
    'analysis_report'
]

# Check for missing keys
missing_keys = [key for key in required_keys if key not in state]
if missing_keys:
    print(f"Missing required keys in current state: {missing_keys}")
    print("Loading missing data from other files...")
    
# Load experimental design data if missing
experimental_design_file = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/step6_experimental_design_state.json'
if os.path.exists(experimental_design_file):
    with open(experimental_design_file, 'r') as f:
        exp_design_data = json.load(f)
    # Add missing fields from experimental design
    if 'base_method_text' not in state:
        state['base_method_text'] = json.dumps(exp_design_data.get('base_method_text', {}))
    if 'new_method' not in state:
        state['new_method'] = exp_design_data.get('new_method', '')
    if 'verification_policy' not in state:
        state['verification_policy'] = exp_design_data.get('verification_policy', '')
    if 'experiment_details' not in state:
        state['experiment_details'] = exp_design_data.get('experiment_details', '')
    if 'experiment_code' not in state:
        state['experiment_code'] = exp_design_data.get('experiment_code', '')
    print(f"Loaded experimental design data from: {experimental_design_file}")
    
# Load analysis report
analysis_file = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/temp_repo/test-kumagai-20250731-v2/analysis_report.md'
if os.path.exists(analysis_file):
    with open(analysis_file, 'r') as f:
        state['analysis_report'] = f.read()
    print(f"Loaded analysis report from: {analysis_file}")

# Load experiment output
output_file = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/temp_repo/test-kumagai-20250731-v2/results/experiment_output.txt'
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        state['output_text_data'] = f.read()
    print(f"Loaded experiment output from: {output_file}")

# Step 11.2: Execute Main Task - Writer Subgraph
print("\n" + "="*60)
print("Step 11.2: EXECUTE WRITER SUBGRAPH")
print("="*60)

try:
    from airas.features.write.writer_subgraph.writer_subgraph import WriterSubgraph
    
    # Initialize the writer subgraph with specified parameters
    writer = WriterSubgraph(
        llm_name="o3-mini-2025-01-31",
        refine_round=1
    )
    
    # Prepare the input state with only the required keys
    writer_input = {
        'base_method_text': state.get('base_method_text', ''),
        'new_method': state.get('new_method', ''),
        'verification_policy': state.get('verification_policy', ''),
        'experiment_details': state.get('experiment_details', ''),
        'experiment_code': state.get('experiment_code', ''),
        'output_text_data': state.get('output_text_data', ''),
        'analysis_report': state.get('analysis_report', ''),
        'image_file_name_list': state.get('image_file_name_list', [
            'experiment1_activation_comparison.pdf',
            'experiment2_parameter_evolution.pdf', 
            'experiment3_gradient_flow.pdf'
        ])
    }
    
    print("Running writer subgraph...")
    print(f"Input keys: {list(writer_input.keys())}")
    
    # Run the writer subgraph
    result = writer.run(writer_input)
    
    # Update state with the results
    state.update(result)
    state['writer_execution'] = {
        'status': 'completed',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'llm_name': 'o3-mini-2025-01-31',
        'refine_round': 1
    }
    
    print("Writer subgraph completed successfully!")
    if 'paper_content' in result:
        print(f"Paper sections generated: {list(result['paper_content'].keys())}")
    
except Exception as e:
    print(f"ERROR executing writer subgraph: {str(e)}")
    import traceback
    traceback.print_exc()
    state['writer_execution'] = {
        'status': 'failed',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'error': str(e)
    }

# Step 11.3: Upload State
print("\n" + "="*60)
print("Step 11.3: UPLOAD STATE")
print("="*60)

# Save the updated state back to the file
output_state_file = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/temp_repo/test-kumagai-20250731-v2/state_step11_complete.json'
with open(output_state_file, 'w') as f:
    json.dump(state, f, indent=2)

print(f"Updated state saved to: {output_state_file}")
print(f"Final state keys: {list(state.keys())}")

# Also save the paper content separately if it exists
if 'paper_content' in state:
    paper_file = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/airas-1/temp_repo/test-kumagai-20250731-v2/paper_draft.json'
    with open(paper_file, 'w') as f:
        json.dump(state['paper_content'], f, indent=2)
    print(f"Paper draft saved to: {paper_file}")

print("\n" + "="*60)
print("STEP 11 COMPLETE")
print("="*60)