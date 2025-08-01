# AIRAS Architecture Clarification

## How AIRAS Works

### Two-Layer Architecture

1. **AIRAS Orchestration Layer** (Runs locally or in MCP server)
   - Executes all the subgraphs in sequence
   - Makes API calls to retrieve papers
   - Uses LLMs to generate methods and code
   - Manages state between steps
   - Triggers GitHub Actions for experiments

2. **Experiment Execution Layer** (Runs on GitHub Actions)
   - Receives generated experiment code from AIRAS
   - Runs the actual ML experiments
   - Produces results (accuracy, graphs, etc.)
   - Uploads artifacts back to the repository

### Current Situation

✅ **What's Working:**
- The Experiment Execution Layer (GitHub Actions) is perfectly set up
- When AIRAS creates experiment code, GitHub Actions runs it successfully
- We saw this work with the AutoGELU experiments

❌ **What's Missing:**
- The AIRAS Orchestration needs to be run for each new research topic
- This orchestration creates different experiments for each branch
- We need to run the orchestration 3 more times (for test-2, test-3, test-4)

### The Correct Flow

```
1. Run AIRAS Orchestration (locally/MCP) for "Quantum algorithms"
   → Creates quantum-inspired optimization method
   → Generates quantum_experiments.py
   → Pushes to test-2 branch
   
2. GitHub Actions automatically runs quantum_experiments.py
   → Produces results
   → Uploads artifacts
   
3. AIRAS Orchestration continues
   → Analyzes results
   → Writes paper
   → Creates HTML
```

### Options to Run AIRAS Orchestration

1. **MCP Server** (Recommended)
   - Configure Claude Desktop with AIRAS MCP
   - Use mcp__airas__ tools directly
   
2. **Local Python** 
   - Need to fix module imports
   - Handle long-running processes
   - Manage API timeouts

3. **Cloud Environment**
   - AWS Lambda, Google Cloud Functions
   - Better for long-running workflows

4. **Manual Step-by-Step**
   - Run each subgraph manually
   - More control but time-consuming

## Summary

- GitHub Actions is already the execution environment for experiments ✅
- We need to run the AIRAS orchestration to create different research for each branch
- Each branch should have completely different generated code and experiments
- The orchestration layer is what creates the diversity, not GitHub Actions