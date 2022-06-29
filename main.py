import os
import argparse
import concurrent.futures
import datetime
import os.path
import shutil
import tarfile
# ------------------------------
# from distutils.extension import Extension
# from distutils.core import setup
# ------------------------------
import time

from setuptools import Extension
from setuptools import setup
import Cython
import Cython.Build
# ------------------------------
from repo import get_git_repo, parse_git_version, parse_workspace_status
from utils import copy_project_to, search_tocompile_files
# ------------------------------
from pprint import pprint
# ----------------------------------------


start_dt = datetime.datetime.now()


# args_parser = argparse.ArgumentParser()
# args_parser.add_argument("src", help="Source directory project in.")
# args_parser.add_argument("-dst", help="Destination directory packaging to.")
# args = args_parser.parse_args()
#
#
# print("src =", args.src)
# print("dst =", args.dst)
# exit()


thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)


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


pkg_info = {}
git_version_info = None
status_flag, status_msg, git_repo = get_git_repo(target_project_dir)
if not status_flag:
    print(status_msg)
    exit()


git_version_info = parse_git_version(git_repo)
pkg_info.update(git_version_info)


clean_flag, workspace_status_info \
    = parse_workspace_status(git_repo)
pkg_info["clean"] = clean_flag
pkg_info["workspace_status"] = workspace_status_info

flag_continue = True
if not clean_flag:
    pprint(pkg_info)
    tip_msg = "工作区不干净,是否继续打包 [y/N]? "
    while True:
        foobar = input(tip_msg)
        if foobar.lower() == "y":
            flag_continue = True
            print("坚持打包!")
            break
        elif (foobar.lower() == "n") or (foobar.lower() == ""):
            flag_continue = False
            print("放弃打包!")
            break
        else:
            tip_msg = "(输入错误!) 工作区不干净,是否继续打包 [y/N]? "
            continue
if not flag_continue:
    exit()


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


def compress_pkg(package_dir: str):
    basename = os.path.basename(package_dir)
    pkg_path = f"{package_dir}.tar.gz"

    with tarfile.open(pkg_path, "x:gz") as tar_gz:
        tar_gz.add(package_dir, arcname=basename)


future = thread_pool.submit(compress_pkg, TARGET_PACKAGE_DIR)
print("开始打 tar.gz 包 ...")
while True:
    if future.done():
        break
    time.sleep(1)
print("打包完成 ...")

