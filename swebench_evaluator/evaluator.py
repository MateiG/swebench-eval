import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
import datasets
import git
import time


class SWEBenchEvaluator:
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or Path.home() / ".swebench_evaluator"
        self.repos_dir = Path(self.cache_dir) / "repos"
        self.dataset = None
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def load_dataset(self):
        self.dataset = datasets.load_dataset("princeton-nlp/SWE-bench_Verified")
        return self.dataset

    def get_problem_by_id(self, instance_id):
        if self.dataset is None:
            self.load_dataset()

        for i in range(len(self.dataset["test"])):
            if self.dataset["test"][i]["instance_id"] == instance_id:
                return self.dataset["test"][i]

        raise ValueError(f"Instance ID {instance_id} not found in the dataset")

    def get_repo_url(self, repo_name):
        return f"https://github.com/{repo_name}.git"

    def clone_or_update_repo(self, repo_name):
        repo_path = self.repos_dir / repo_name.replace("/", "_")
        repo_url = self.get_repo_url(repo_name)

        if repo_path.exists():
            try:
                repo = git.Repo(repo_path)
                repo.git.fetch(all=True)
            except Exception:
                shutil.rmtree(repo_path, ignore_errors=True)
                repo = git.Repo.clone_from(repo_url, repo_path)
        else:
            repo = git.Repo.clone_from(repo_url, repo_path)

        return repo_path

    def get_python_executable(self, repo_path):
        """
        Check for common virtual environment directories within the repository.
        Return the path to the Python executable if found, otherwise fall back to 'python'.
        """
        possible_dirs = [".venv", "venv", "env"]
        for d in possible_dirs:
            venv_dir = repo_path / d
            if venv_dir.exists() and venv_dir.is_dir():
                # For Unix-like systems
                candidate = venv_dir / "bin" / "python"
                if candidate.exists():
                    return str(candidate)
                # For Windows environments
                candidate = venv_dir / "Scripts" / "python.exe"
                if candidate.exists():
                    return str(candidate)
        return "python"

    def run_tests(self, repo_path, tests, timeout=300):
        results = {}
        repo_path = Path(repo_path)

        # Determine the appropriate Python executable
        python_executable = self.get_python_executable(repo_path)
        print(f"Using Python executable: {python_executable}")

        for test in tests:
            print(f"Running test: {test}")
            try:
                start_time = time.time()
                process = subprocess.run(
                    f"{python_executable} -m pytest {test} -v",
                    cwd=repo_path,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                duration = time.time() - start_time

                passed = process.returncode == 0
                results[test] = {
                    "passed": passed,
                    "returncode": process.returncode,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "duration": duration,
                }
                status = "PASSED" if passed else "FAILED"
                print(f"Test {test}: {status}")
            except subprocess.TimeoutExpired:
                print(f"Test {test} timed out after {timeout} seconds")
                results[test] = {
                    "passed": False,
                    "error": "timeout",
                    "duration": timeout,
                }
            except Exception as e:
                print(f"Error running test {test}: {e}")
                results[test] = {"passed": False, "error": str(e), "duration": 0}

        return results

    def evaluate_solution(self, instance_id, solution_commit):
        problem = self.get_problem_by_id(instance_id)
        repo_name = problem["repo"]
        base_commit = problem["base_commit"]

        fail_to_pass_tests = json.loads(problem["FAIL_TO_PASS"])
        pass_to_pass_tests = json.loads(problem["PASS_TO_PASS"])

        repo_path = self.clone_or_update_repo(repo_name)
        repo = git.Repo(repo_path)

        results = {
            "instance_id": instance_id,
            "repo": repo_name,
            "base_commit": base_commit,
            "solution_commit": solution_commit,
            "timestamp": time.time(),
            "before": {"fail_to_pass": {}, "pass_to_pass": {}},
            "after": {"fail_to_pass": {}, "pass_to_pass": {}},
            "metrics": {
                "fixed_tests": 0,
                "broken_tests": 0,
                "total_tests": len(fail_to_pass_tests) + len(pass_to_pass_tests),
                "success_rate": 0.0,
            },
        }

        try:
            print(f"Checking out base commit {base_commit}...")
            repo.git.checkout(base_commit, force=True)

            print(f"Running tests on base commit...")
            results["before"]["fail_to_pass"] = self.run_tests(
                repo_path, fail_to_pass_tests
            )
            results["before"]["pass_to_pass"] = self.run_tests(
                repo_path, pass_to_pass_tests
            )

            print(f"Checking out solution commit {solution_commit}...")
            repo.git.checkout(solution_commit, force=True)

            print(f"Running tests on solution commit...")
            results["after"]["fail_to_pass"] = self.run_tests(
                repo_path, fail_to_pass_tests
            )
            results["after"]["pass_to_pass"] = self.run_tests(
                repo_path, pass_to_pass_tests
            )

            fixed_tests = sum(
                1
                for test in fail_to_pass_tests
                if not results["before"]["fail_to_pass"]
                .get(test, {})
                .get("passed", False)
                and results["after"]["fail_to_pass"].get(test, {}).get("passed", False)
            )

            broken_tests = sum(
                1
                for test in pass_to_pass_tests
                if results["before"]["pass_to_pass"].get(test, {}).get("passed", False)
                and not results["after"]["pass_to_pass"]
                .get(test, {})
                .get("passed", False)
            )

            results["metrics"]["fixed_tests"] = fixed_tests
            results["metrics"]["broken_tests"] = broken_tests
            results["metrics"]["success_rate"] = (
                fixed_tests / len(fail_to_pass_tests) if fail_to_pass_tests else 1.0
            )

            print("\nEvaluation results:")
            print(f"Fixed tests: {fixed_tests}/{len(fail_to_pass_tests)}")
            print(f"Broken tests: {broken_tests}/{len(pass_to_pass_tests)}")
            print(f"Success rate: {results['metrics']['success_rate']:.2%}")

        except Exception as e:
            print(f"Error during evaluation: {e}")
            results["error"] = str(e)

        return results

    def setup_for_development(self, instance_id, output_dir=None):
        if output_dir is None:
            output_dir = Path.cwd() / "swebench_workdir"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        problem = self.get_problem_by_id(instance_id)
        repo_name = problem["repo"]
        base_commit = problem["base_commit"]

        repo_url = self.get_repo_url(repo_name)
        repo_path = output_dir / repo_name.split("/")[-1]

        if repo_path.exists():
            print(f"Repository already exists at {repo_path}, removing...")
            shutil.rmtree(repo_path)

        print(f"Cloning {repo_url} to {repo_path}...")
        repo = git.Repo.clone_from(repo_url, repo_path)

        print(f"Checking out base commit {base_commit}...")
        repo.git.checkout(base_commit, force=True)

        print(f"\nRepository setup complete!")
        print(f"Working directory: {repo_path}")
        print(f"Tests that need to be fixed:")
        for test in json.loads(problem["FAIL_TO_PASS"]):
            print(f"  - {test}")

        return {
            "instance_id": instance_id,
            "repo_path": str(repo_path),
            "base_commit": base_commit,
            "fail_to_pass_tests": json.loads(problem["FAIL_TO_PASS"]),
            "pass_to_pass_tests": json.loads(problem["PASS_TO_PASS"]),
        }

    def get_problem_details(self, instance_id, include_patch=False):
        problem = self.get_problem_by_id(instance_id)

        problem_statement = problem["problem_statement"].strip()
        fail_to_pass = json.loads(problem["FAIL_TO_PASS"])
        pass_to_pass = json.loads(problem["PASS_TO_PASS"])

        fail_tests_by_file = {}
        for test in fail_to_pass:
            parts = test.split("::")
            if len(parts) >= 2:
                file_path, test_name = parts[0], "::".join(parts[1:])
                if file_path not in fail_tests_by_file:
                    fail_tests_by_file[file_path] = []
                fail_tests_by_file[file_path].append(test_name)

        details = {
            "instance_id": problem["instance_id"],
            "repo": problem["repo"],
            "problem_statement": problem_statement,
            "base_commit": problem["base_commit"],
            "failing_tests": fail_tests_by_file,
            "fail_to_pass_tests": fail_to_pass,
            "pass_to_pass_tests": pass_to_pass,
            "created_at": problem["created_at"],
        }

        if include_patch:
            details["patch"] = problem["patch"]
            details["test_patch"] = problem["test_patch"]

        if problem["hints_text"] and problem["hints_text"].strip():
            details["hints"] = problem["hints_text"].strip()

        return details

    def get_benchmark_summary(self, repo=None):
        if self.dataset is None:
            self.load_dataset()

        if repo:
            problem_ids = [
                record["instance_id"]
                for record in self.dataset["test"]
                if record["repo"] == repo
            ]
            return {"repo": repo, "problem_ids": problem_ids}

        sample_problems = []
        for i in range(min(5, len(self.dataset["test"]))):
            sample_problems.append(self.dataset["test"][i]["instance_id"])

        repositories = set()
        for i in range(len(self.dataset["test"])):
            repositories.add(self.dataset["test"][i]["repo"])

        return {
            "total_problems": len(self.dataset["test"]),
            "repositories": list(repositories),
            "sample_problems": sample_problems,
        }
