import os
import time
import datetime
import os.path
import shutil
# from distutils.extension import Extension
# from distutils.core import setup
from pprint import pprint
# ------------------------------
from setuptools import Extension
from setuptools import setup
import Cython
import Cython.Build
# ------------------------------
from repo import get_git_repo, parse_git_version
from utils import copy_project_to, search_tocompile_files
# ----------------------------------------


start_dt = datetime.datetime.now()


TARGET_PROJECT_DIR = "/home/jskj/Desktop/tmp/MXT_QC_TopTally"
TARGET_PACKAGE_DIR = "/home/jskj/Desktop/tmp/package"

USE_THREADS = True


target_project_dir = os.path.abspath(TARGET_PROJECT_DIR)
if not os.path.isdir(target_project_dir):
    print("目标项目路径必须是一个目录")
    exit()
target_package_dir = os.path.abspath(TARGET_PACKAGE_DIR)
if os.path.exists(target_package_dir):
    os.rename(target_package_dir, 
              target_package_dir+f"-{start_dt.strftime('%Y%m%d%H%M%S.%f')}")
os.makedirs(target_package_dir)

target_project_dir_stat = os.stat(target_project_dir)
target_package_dir_stat = os.stat(target_package_dir)
flag_using_link = False
if target_project_dir_stat.st_dev == target_package_dir_stat:
    flag_using_link = True


if USE_THREADS:
    n_threads = os.cpu_count()
else:
    n_threads = 0


git_version_info = None
status_flag, status_msg, git_repo = get_git_repo(target_project_dir)
if not status_flag:
    print(status_msg)
    exit()
else:
    git_version_info = parse_git_version(git_repo)

pprint(git_version_info)


flag_root_dir_has_init_pyfile \
    = copy_project_to(target_project_dir, target_package_dir, flag_using_link)

assert flag_root_dir_has_init_pyfile == True

exclude_file_relpath_list = ["top_vision.py"]
# exclude_dir_relpath_list = ["algorithms"]
exclude_dir_relpath_list = ["configs"]
tocompile_file_list, tocompile_cfile_list \
    = search_tocompile_files(target_package_dir, 
                             # exclude_files=[os.path.join(target_package_dir, exclude_file_relpath) 
                             #                for exclude_file_relpath in exclude_file_relpath_list],
                             exclude_files=exclude_file_relpath_list,
                             # exclude_dirs=[os.path.join(target_package_dir, exclude_dir_relpath)
                             #               for exclude_dir_relpath in exclude_dir_relpath_list],
                             exclude_dirs=exclude_dir_relpath_list)


def cythonize_files(target_package_dir: str, to_compile_file_list: list, n_threads=0) -> list:
    pprint(to_compile_file_list)
    orig_cwd = os.getcwd()
    os.chdir(target_package_dir)

    # cythonized_extension_list = []
    # for tocompile_file in tocompile_file_list:
    #     cythonized_extension = Cython.Build.cythonize(tocompile_file,
    #                                                   compiler_directives={'language_level': "3"})
    #     cythonized_extension_list.extend(cythonized_extension)

    cythonized_extension_list \
        = Cython.Build.cythonize(tocompile_file_list,
                                 compiler_directives={'language_level': "3"},
                                 nthreads=n_threads)
    
    os.chdir(orig_cwd)
    return cythonized_extension_list


cythonized_extension_list = cythonize_files(target_package_dir, tocompile_file_list,
                                            n_threads=n_threads)

if flag_root_dir_has_init_pyfile:
    os.rename(os.path.join(target_package_dir, "__init__pyfile"),
              os.path.join(target_package_dir, "__init__.py"))


os.chdir(target_package_dir)

setup(
    ext_modules=cythonized_extension_list,
    script_args=["build_ext", "--inplace"] + ["-j", f"{n_threads}"] if n_threads else [],
    zip_safe=False,
)


for filepath in tocompile_file_list:
    os.remove(filepath)
for c_filepath in tocompile_cfile_list:
    os.remove(c_filepath)

shutil.rmtree(os.path.join(target_package_dir, "build"))
