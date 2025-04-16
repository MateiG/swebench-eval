# print_project.py
import os
import pyperclip


def get_structure_and_contents(
    directory, ignored_dirs=None, ignored_files=None, prefix=""
):
    if ignored_dirs is None:
        ignored_dirs = ["venv", "__pycache__", ".pytest_cache", "repos"]
    if ignored_files is None:
        ignored_files = ["__init__.py", ".DS_Store"]

    output = []
    try:
        items = sorted(os.listdir(directory))
        items = [
            item
            for item in items
            if item not in ignored_dirs and item not in ignored_files
        ]

        for index, item in enumerate(items):
            item_path = os.path.join(directory, item)
            is_last = index == len(items) - 1
            connector = "└── " if is_last else "├── "

            if os.path.isdir(item_path):
                output.append(prefix + connector + f"[DIR] {item}")
                new_prefix = prefix + ("    " if is_last else "│   ")
                output.extend(
                    get_structure_and_contents(
                        item_path, ignored_dirs, ignored_files, new_prefix
                    )
                )
            elif os.path.isfile(item_path):
                output.append(prefix + connector + f"[FILE] {item}")
                output.extend(
                    get_file_contents(
                        item_path, prefix + ("    " if is_last else "│   ")
                    )
                )
    except PermissionError:
        output.append(prefix + "[ACCESS DENIED]")
    return output


def get_file_contents(file_path, prefix):
    output = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
            for line in content.splitlines():
                output.append(prefix + "│   " + line)
    except Exception as e:
        output.append(prefix + f"[ERROR READING FILE] {e}")
    return output


if __name__ == "__main__":
    root_dir = "."
    structure_output = []
    structure_output.extend(get_structure_and_contents(root_dir))
    result = "\n".join(structure_output)
    pyperclip.copy(result)
    print("Directory structure copied to clipboard.")
