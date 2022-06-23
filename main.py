import os
import os.path
from distutils.core import setup
from pprint import pprint
import shutil
# ------------------------------
import Cython
import Cython.Build
# ------------------------------
from repo import get_git_repo, parse_git_version
from utils import copy_project_to, search_tocompile_files
# ----------------------------------------


TARGET_PROJECT_DIR = "/data/projects/wai4/MXT_QC_TopTally"
TARGET_PACKAGE_DIR = "/home/jskj/Desktop/tmp/MXT_QC_TopTally"


target_project_dir = os.path.abspath(TARGET_PROJECT_DIR)
if not os.path.isdir(target_project_dir):
    print("目标项目路径必须是一个目录")
    exit()
target_package_dir = os.path.abspath(TARGET_PACKAGE_DIR)
os.makedirs(target_package_dir)

target_project_dir_stat = os.stat(target_project_dir)
target_package_dir_stat = os.stat(target_package_dir)
flag_using_link = False
if target_project_dir_stat.st_dev == target_package_dir_stat:
    flag_using_link = True


git_version_info = None
status_flag, status_msg, git_repo = get_git_repo(target_project_dir)
if not status_flag:
    print(status_msg)
    exit()
else:
    git_version_info = parse_git_version(git_repo)

pprint(git_version_info)


copy_project_to(target_project_dir, target_package_dir, flag_using_link)

exclude_file_relpath_list = ["top_vision.py"]
exclude_dir_relpath_list = ["algorithms"]
tocompile_file_list = search_tocompile_files(target_package_dir, 
                                             exclude_files=[os.path.join(target_package_dir, exclude_file_relpath) 
                                                            for exclude_file_relpath in exclude_file_relpath_list],
                                             exclude_dirs=[os.path.join(target_package_dir, exclude_dir_relpath)
                                                           for exclude_dir_relpath in exclude_dir_relpath_list])

pprint(tocompile_file_list)

os.chdir(target_package_dir)
cythonized_extension = Cython.Build.cythonize(tocompile_file_list, 
                                              compiler_directives={'language_level': "3"})

for filepath in tocompile_file_list:
    os.remove(filepath)

setup(ext_modules=cythonized_extension)

shutil.rmtree(os.path.join(target_package_dir, "build"))