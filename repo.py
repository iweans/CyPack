import datetime
import dulwich
import dulwich.repo
import dulwich.objects
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
        git_repo = dulwich.repo.Repo(repo_path)
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
    git_commit: dulwich.objects.Commit = git_repo.get_object(git_head_hash)
    git_commit_time = git_commit.commit_time
    git_commit_datetime = datetime.datetime.fromtimestamp(git_commit_time)
    git_describe = porcelain.describe(git_repo)
    # ------------------------------
    return {
        "branch": git_branch.decode(),
        "head": git_head_hash.decode(),
        "tag": git_describe,
        "commit_timestamp": git_commit_time,
        "commit_datetime": git_commit_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    }


def parse_workspace_status(git_repo: dulwich.repo.Repo) -> tuple:
    """

    """
    # ----------------------------------------
    flag_is_clean = True
    # ------------------------------
    git_status = porcelain.status(git_repo)
    staged_dict = git_status.staged
    add_list = staged_dict["add"]
    if add_list:
        flag_is_clean = False
    delete_list = staged_dict["delete"]
    if delete_list:
        flag_is_clean = False
    modify_list = staged_dict["modify"]
    if modify_list:
        flag_is_clean = False
    # ------------------------------
    unstaged_list = git_status.unstaged
    if unstaged_list:
        flag_is_clean = False
    untracked_list = git_status.untracked
    if untracked_list:
        flag_is_clean = False
    # ------------------------------
    return flag_is_clean, {
        "add": [i.decode() for i in add_list],
        "delete": [i.decode() for i in delete_list],
        "modify": [i.decode() for i in modify_list],
        "unstaged": [i.decode() for i in unstaged_list],
        "untracked": [i.decode() for i in untracked_list]
    }

