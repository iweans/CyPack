import dulwich
import dulwich.repo
from dulwich import porcelain
import dulwich.errors
# ------------------------------
# ----------------------------------------


def get_git_repo(repo_path: str) -> tuple:
    """
    说明: 
    """
    # ----------------------------------------
    status_flag = False
    status_msg = ""
    git_repo = None
    # ------------------------------
    try:
        git_repo = dulwich.repo.Repo(target_project_dir)
    except dulwich.errors.NotGitRepository:
        status_msg = "该项目没有被Git所管理"
    else:
        status_flag = True
    # ------------------------------
    return status_flag, status_msg, git_repo


def parse_git_version(git_repo: dulwich.repo.Repo) -> dict:
    """
    """
    # ----------------------------------------
    git_branch = porcelain.active_branch(git_repo)
    git_head_hash = git_repo.head()
    git_describe = porcelain.describe(git_repo)
    # ------------------------------
    return {
        "branch": git_branch, 
        "head": git_head_hash, 
        "tag": git_describe,
    }
