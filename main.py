import os
from pprint import pprint
# ------------------------------
# ------------------------------
from .repo import get_git_repo, parse_git_version
# ----------------------------------------


TARGET_PROJECT_DIR = "/data/projects/wai4/MXT_QC_TopTally"
TARGET_PACKAGE_DIR = "/home/jskj/Desktop/MXT_QC_TopTally"


target_project_dir = os.path.abspath(TARGET_PROJECT_DIR)

git_version_info = None
status_flag, status_msg, git_repo = get_git_repo(target_project_dir)
if not status_flag:
    print(status_msg)
    exit()
else:
    git_version_info = parse_git_version(git_repo)

pprint(git_version_info)




