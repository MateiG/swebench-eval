# SWE-Bench Evaluator

A powerful framework for evaluating AI-assisted developer tools on real-world programming challenges from the SWE-bench Verified dataset.

## 🚀 What is SWE-Bench Evaluator?

SWE-Bench Evaluator provides a systematic way to assess how effectively AI coding assistants (such as GitHub Copilot, Cursor, Windsurf, and others) help developers solve actual GitHub issues. By using real bugs from open-source projects that have been verified as fixed, this tool offers an objective measure of AI assistant performance.

## ✨ Key Features

- **Real-world Testing**: Evaluate AI tools against actual GitHub issues with verified solutions
- **Comprehensive Metrics**: Track success rates, test fixes, and regressions
- **Streamlined Workflow**: Simple CLI commands for browsing, selecting, and evaluating challenges
- **Batch Processing**: Run multiple evaluations in parallel with configurable settings
- **Detailed Reports**: Generate structured output for comparing different AI assistants

## 📋 Prerequisites

- Python 3.7+
- Git

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/swebench-evaluator.git
cd swebench-evaluator

# Install the package
pip install -e .
```

## 📘 Usage Guide

### Discovering Available Challenges

View all available challenges in the SWE-bench Verified dataset:

```bash
swebench-eval list
```

### Exploring a Specific Challenge

Get detailed information about a particular challenge:

```bash
swebench-eval details astropy__astropy-12907
```

Add the `--include-patch` flag to see the reference solution:

```bash
swebench-eval details astropy__astropy-12907 --include-patch
```

### Setting Up a Development Environment

Set up a repository at the exact commit where the issue exists:

```bash
swebench-eval setup astropy__astropy-12907 --output-dir ./my-workdir
```

This will:

1. Clone the repository
2. Check out the correct commit
3. Show which tests need to be fixed

### Evaluating a Solution

After working with an AI assistant to solve the problem and committing your changes:

```bash
swebench-eval evaluate astropy__astropy-12907 your-solution-commit-hash
```

The evaluation will:

1. Run the failing tests on the base commit to verify they fail
2. Switch to your solution commit
3. Run the tests again to see if your changes fixed the issue
4. Verify no regressions were introduced
5. Produce a detailed report with metrics

### Batch Evaluation

For evaluating multiple solutions at once, create a JSON configuration file:

```json
[
  {
    "instance_id": "astropy__astropy-12907",
    "solution_commit": "abcd1234",
    "tool": "GitHub Copilot"
  },
  {
    "instance_id": "astropy__astropy-13033",
    "solution_commit": "efgh5678",
    "tool": "Cursor"
  }
]
```

Then run the batch evaluation:

```bash
swebench-eval batch config.json --output-dir ./results
```

## Complete Workflow

1. **Browse challenges**:

   ```bash
   swebench-eval list
   ```

2. **Choose a challenge**:

   ```bash
   swebench-eval details astropy__astropy-12907
   ```

3. **Set up the development environment**:

   ```bash
   swebench-eval setup astropy__astropy-12907 --output-dir ./workdir
   ```

4. **Work with an AI assistant** to implement a fix

   - Provide the GitHub issue description to the assistant
   - Collaborate to create a solution

5. **Commit your solution**:

   ```bash
   git add .
   git commit -m "Fix with GitHub Copilot"
   ```

6. **Evaluate the solution**:

   ```bash
   swebench-eval evaluate astropy__astropy-12907 $(git rev-parse HEAD)
   ```

7. **Compare results** across different AI assistants
