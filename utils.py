import os
import os.path
import glob
import shutil

from isort import file


def copy_project_to(src_dir: str, dst_dir: str,
                    using_link=False) -> bool:
    """
    """
    # ----------------------------------------
    # ------------------------------
    hidden_reldirpath_stack = []
    for src_dirpath, src_subdirname_list, src_subfilename_list in os.walk(src_dir):
        src_dirname = os.path.basename(src_dirpath)
        src_reldirpath = os.path.relpath(src_dirpath, start=src_dir)
        # --------------------
        if len(hidden_reldirpath_stack):
            if src_reldirpath.startswith(hidden_reldirpath_stack[-1]):
                continue
            else:
                hidden_reldirpath_stack.pop()
        # --------------------
        if src_dirname.startswith(".") \
                or (src_dirname == "__pycache__"):
            hidden_reldirpath_stack.append(src_reldirpath)
            continue
        # --------------------
        # 创建对应的目录
        dst_dirpath = os.path.join(dst_dir, src_reldirpath)
        if src_reldirpath != ".":
            os.mkdir(dst_dirpath)
        # 复制目录的子文件
        for src_filename in src_subfilename_list:
            src_filepath = os.path.join(src_dirpath, src_filename)
            dst_filepath = os.path.join(dst_dirpath, src_filename)
            if os.path.islink(src_filepath):
                link_to = os.readlink(src_filepath)
                os.symlink(link_to, dst_filepath)
            elif using_link:
                os.link(src_filepath, dst_filepath)
            else:
                shutil.copy(src_filepath, dst_filepath)
    return True


def search_tocompile_files(search_dir: str, 
                           exclude_files=None, exclude_dirs=None) -> list:
    exclude_file_list = exclude_files or []
    exclude_dir_list = exclude_dirs or []

    search_ext_list = [
        "py", "pY", "Py", "PY", 
        "pyx", "pyX", "pYx", "pYX", "Pyx", "PyX", "PYx", "PYX",
    ]

    tocompile_file_list = []
    for search_ext in search_ext_list:
        search_glob_pattern = os.path.join(search_dir, f"**/*.{search_ext}")
        for filepath in glob.iglob(search_glob_pattern, recursive=True):
            filename = os.path.basename(filepath)
            lowcase_filename = filename.lower()
            if (lowcase_filename == "setup.py") \
                    or (lowcase_filename == "__init__.py"):
                continue
            
            if filepath in exclude_file_list:
                continue
            flag_in_exclude_dir = False
            for exclude_dirpath in exclude_dir_list:
                if filepath.startswith(exclude_dirpath):
                    flag_in_exclude_dir = True
                    break
            if flag_in_exclude_dir:
                continue

            tocompile_file_list.append(filepath)

    return tocompile_file_list

