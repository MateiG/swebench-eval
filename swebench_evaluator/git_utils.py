import os
from pathlib import Path
import git


def ensure_repo(repo_url, repo_path):
    if os.path.exists(repo_path):
        try:
            repo = git.Repo(repo_path)
            repo.git.fetch(all=True)
            return repo
        except git.InvalidGitRepositoryError:
            import shutil

            shutil.rmtree(repo_path)

    return git.Repo.clone_from(repo_url, repo_path)


def checkout_commit(repo, commit_hash, force=True):
    repo.git.checkout(commit_hash, force=force)


def apply_patch(repo, patch_content):
    patch_path = os.path.join(repo.working_dir, "temp.patch")
    try:
        with open(patch_path, "w") as f:
            f.write(patch_content)

        repo.git.apply(patch_path)
        return True
    except git.GitCommandError:
        return False
    finally:
        if os.path.exists(patch_path):
            os.remove(patch_path)


def get_changed_files(repo, commit_hash):
    changed_files = []
    try:
        commit = repo.commit(commit_hash)
        parents = commit.parents

        if not parents:
            return [item.path for item in commit.tree.traverse()]

        parent = parents[0]
        diff = parent.diff(commit)

        for diff_item in diff:
            if diff_item.a_path:
                changed_files.append(diff_item.a_path)
            if diff_item.b_path and diff_item.b_path != diff_item.a_path:
                changed_files.append(diff_item.b_path)

        return list(set(changed_files))
    except git.GitCommandError:
        return []
