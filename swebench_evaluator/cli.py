#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path

from swebench_evaluator.evaluator import SWEBenchEvaluator


def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Evaluate AI-assisted developer tools using SWE-bench Verified dataset"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    list_parser = subparsers.add_parser(
        "list", help="List available benchmark problems"
    )
    list_parser.add_argument(
        "--output", "-o", help="Output file for the problem list (JSON format)"
    )
    list_parser.add_argument(
        "--repo", help="Print out all problem IDs for the specified repository"
    )

    details_parser = subparsers.add_parser(
        "details", help="Show details of a specific problem"
    )
    details_parser.add_argument("instance_id", help="Instance ID of the problem")
    details_parser.add_argument(
        "--include-patch", "-p", action="store_true", help="Include reference patch"
    )
    details_parser.add_argument(
        "--output", "-o", help="Output file for the problem details (JSON format)"
    )

    setup_parser = subparsers.add_parser(
        "setup", help="Set up a repository for development"
    )
    setup_parser.add_argument("instance_id", help="Instance ID of the problem")
    setup_parser.add_argument(
        "--output-dir", "-o", help="Directory to set up repository in"
    )

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate a solution for a specific problem"
    )
    evaluate_parser.add_argument("instance_id", help="Instance ID of the problem")
    evaluate_parser.add_argument(
        "solution_commit", help="Git commit hash of the solution to evaluate"
    )
    evaluate_parser.add_argument(
        "--output", "-o", help="Output file for the evaluation results (JSON format)"
    )

    batch_parser = subparsers.add_parser(
        "batch", help="Batch evaluate multiple solutions"
    )
    batch_parser.add_argument(
        "config_file", help="JSON file with evaluation configurations"
    )
    batch_parser.add_argument(
        "--output-dir",
        "-o",
        default="./results",
        help="Directory for outputting results",
    )

    for subparser in [
        list_parser,
        details_parser,
        setup_parser,
        evaluate_parser,
        batch_parser,
    ]:
        subparser.add_argument(
            "--cache-dir", help="Directory to cache repositories and dataset"
        )

    return parser


def print_json(data, output_file=None):
    if output_file:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {output_file}")
    else:
        print(json.dumps(data, indent=2))


def list_problems(evaluator: SWEBenchEvaluator, args):
    if args.repo:
        summary = evaluator.get_benchmark_summary(repo=args.repo)
    else:
        summary = evaluator.get_benchmark_summary()
    print_json(summary, args.output)


def show_problem_details(evaluator: SWEBenchEvaluator, args):
    details = evaluator.get_problem_details(
        args.instance_id, include_patch=args.include_patch
    )

    if args.output:
        with open(args.output, "w") as f:
            json.dump(details, f, indent=2)
        print(f"Details saved to {args.output}")
    else:
        print(f"\n{'=' * 80}")
        print(f"Problem: {details['instance_id']}")
        print(f"Repository: {details['repo']}")
        print(f"{'=' * 80}\n")

        print("PROBLEM DESCRIPTION:")
        print(f"{details['problem_statement']}\n")

        print(f"BASE COMMIT: {details['base_commit']}")
        print(f"CREATED: {details['created_at']}\n")

        print("FAILING TESTS TO FIX:")
        for file_path, tests in details["failing_tests"].items():
            print(f"  File: {file_path}")
            for test in tests:
                print(f"    - {test}")
        print()

        if "hints" in details:
            print("HINTS:")
            print(details["hints"])
            print()

        if args.include_patch:
            print("REFERENCE PATCH:")
            print(details["patch"])
            print()


def setup_for_development(evaluator: SWEBenchEvaluator, args):
    setup_info = evaluator.setup_for_development(
        args.instance_id, output_dir=args.output_dir
    )
    print_json(setup_info)


def evaluate_solution(evaluator: SWEBenchEvaluator, args):
    results = evaluator.evaluate_solution(args.instance_id, args.solution_commit)
    print_json(results, args.output)


def batch_evaluate(evaluator: SWEBenchEvaluator, args):
    with open(args.config_file, "r") as f:
        configs = json.load(f)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, config in enumerate(configs):
        print(f"Evaluating {i+1}/{len(configs)}: {config['instance_id']}")
        results = evaluator.evaluate_solution(
            config["instance_id"], config["solution_commit"]
        )
        output_file = (
            output_dir / f"{config['instance_id']}_{int(results['timestamp'])}.json"
        )
        print_json(results, str(output_file))


def main():
    parser = setup_argparse()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    evaluator = SWEBenchEvaluator(cache_dir=args.cache_dir)

    if args.command == "list":
        list_problems(evaluator, args)
    elif args.command == "details":
        show_problem_details(evaluator, args)
    elif args.command == "setup":
        setup_for_development(evaluator, args)
    elif args.command == "evaluate":
        evaluate_solution(evaluator, args)
    elif args.command == "batch":
        batch_evaluate(evaluator, args)


if __name__ == "__main__":
    main()
