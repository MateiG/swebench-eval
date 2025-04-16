from setuptools import setup, find_packages

setup(
    name="swebench-evaluator",
    version="0.1.0",
    description="Evaluation framework for AI-assisted developer tools using SWE-bench",
    author="AI Tools Evaluator",
    packages=find_packages(),
    install_requires=[
        "datasets>=2.0.0",
        "gitpython>=3.1.0",
        "pytest>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "swebench-eval=swebench_evaluator.cli:main",
        ],
    },
    python_requires=">=3.7",
)
