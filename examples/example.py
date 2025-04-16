#!/usr/bin/env python3
import sys
from swebench_evaluator import SWEBenchEvaluator


def main():
    evaluator = SWEBenchEvaluator()
    evaluator.load_dataset()

    # Print dataset summary
    summary = evaluator.get_benchmark_summary()
    print(f"Total problems: {summary['total_problems']}")
    print(f"Sample problems: {', '.join(summary['sample_problems'])}")
    print()

    # Get details for a specific problem
    instance_id = "astropy__astropy-12907"
    details = evaluator.get_problem_details(instance_id)
    print(f"Repository: {details['repo']}")
    print(f"Base commit: {details['base_commit']}")
    print(f"Tests to fix: {len(details['fail_to_pass_tests'])}")
    print()

    # To set up for development:
    # setup_info = evaluator.setup_for_development(instance_id, "./workdir")
    # print(f"Repository set up at: {setup_info['repo_path']}")

    # To evaluate a solution:
    # results = evaluator.evaluate_solution(instance_id, "your-commit-hash")
    # print(f"Fixed tests: {results['metrics']['fixed_tests']}")
    # print(f"Success rate: {results['metrics']['success_rate']}")


if __name__ == "__main__":
    main()
