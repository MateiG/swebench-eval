# Using SWE-bench to Test Windsurf

This guide outlines the steps to use SWE-bench evaluator for testing the Windsurf AI coding assistant against specific GitHub PRs.

## Overview of Steps

1. Setup the SWE-bench evaluator
2. List and explore the problems (including specific PRs)
3. Set up a problem for development
4. Use Windsurf to create a solution
5. Evaluate the solution

## Step-by-Step Guide

### 1. Install SWE-bench evaluator

```bash
git clone https://github.com/MateiG/swebench-eval.git
cd swebench-eval
pip install -e .
```

### 2. List Available Problems

```bash
swebench-eval list
```

### 3. View Details for Specific PR Problems

For each PR reference:

```bash
swebench-eval details scikit-learn__scikit-learn-10297
swebench-eval details scikit-learn__scikit-learn-10844
swebench-eval details scikit-learn__scikit-learn-10908
swebench-eval details psf__requests-1142
swebench-eval details psf__requests-6028
```

### 4. Set Up Development Environment for a Problem

Choose one of the problems to work on:

```bash
swebench-eval setup scikit-learn__scikit-learn-10297 --output-dir ./workspace
```

This will:
- Clone the repository
- Checkout the base commit (before the fix)
- Provide information about failing tests

### 5. Use Windsurf to Solve the Problem

1. Open the workspace directory in Windsurf
2. Use Windsurf to help you fix the failing tests
3. Commit your changes

### 6. Evaluate Your Solution

```bash
swebench-eval evaluate scikit-learn__scikit-learn-10297 YOUR_COMMIT_HASH
```

### 7. Batch Evaluation (Optional)

To evaluate multiple solutions at once, create a JSON config file:

```json
[
  {
    "instance_id": "scikit-learn__scikit-learn-10297",
    "solution_commit": "COMMIT_HASH_1"
  },
  {
    "instance_id": "scikit-learn__scikit-learn-10844",
    "solution_commit": "COMMIT_HASH_2"
  }
]
```

Then run:
```bash
swebench-eval batch config.json --output-dir ./results
```

## Notes

- The PR references (like `scikit-learn__scikit-learn-10297`) are instance IDs in the SWE-bench dataset
- Each instance represents a real bug that was fixed in the actual project
- The evaluation measures if your AI-assisted solution passes the tests that were failing before
- SWE-bench loads the dataset from "princeton-nlp/SWE-bench_Verified"
