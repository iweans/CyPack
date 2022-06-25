import os
import os.path
import glob
import shutil

from isort import file
from pytools import to_uncomplex_dtype


_tocompile_ext_list = [
    "py", "pY", "Py", "PY", 
    "pyx", "pyX", "pYx", "pYX", "Pyx", "PyX", "PYx", "PYX",
]


def copy_project_to(src_dir: str, dst_dir: str,
                    using_link=False) -> bool:
    """
    """
    # ----------------------------------------
    # ------------------------------
    flag_root_dir_has_init_pyfile = False
    hidden_reldirpath_stack = []
    for src_dirpath, src_subdirname_list, src_subfilename_list in os.walk(src_dir):
        src_dirname = os.path.basename(src_dirpath)
        src_reldirpath = os.path.relpath(src_dirpath, start=src_dir)

        flag_is_root_dir = (src_reldirpath == ".")
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
        if not flag_is_root_dir:
            os.mkdir(dst_dirpath)

        # 复制目录的子文件
        flag_has_init_pyfile = False
        flag_has_tocompile_file = False
        for src_filename in src_subfilename_list:
            pure_name, ext = os.path.splitext(src_filename)
            if src_filename == "__init__.py":
                flag_has_init_pyfile = True
                if flag_is_root_dir:
                    flag_root_dir_has_init_pyfile = True
            elif len(ext)>1 \
                    and ext[1:] in _tocompile_ext_list:
                flag_has_tocompile_file = True
            src_filepath = os.path.join(src_dirpath, src_filename)
            dst_filepath = os.path.join(dst_dirpath, src_filename)
            if os.path.islink(src_filepath):
                link_to = os.readlink(src_filepath)
                os.symlink(link_to, dst_filepath)
            elif using_link:
                os.link(src_filepath, dst_filepath)
            else:
                shutil.copy(src_filepath, dst_filepath)
        
        if not flag_is_root_dir \
                and not flag_has_init_pyfile \
                and flag_has_tocompile_file:
            dst_init_py_file_path = os.path.join(dst_dirpath, "__init__.py")
            with open(dst_init_py_file_path, "w") as f:
                f.flush()
        
        if flag_is_root_dir \
                and flag_root_dir_has_init_pyfile:
            os.rename(os.path.join(dst_dirpath, "__init__.py"),
                      os.path.join(dst_dirpath, "__init__pyfile"))

    return flag_root_dir_has_init_pyfile


def search_tocompile_files(search_dir: str, 
                           exclude_files=None, exclude_dirs=None) -> tuple:
    orig_cwd = os.getcwd()
    os.chdir(search_dir)

    exclude_file_list = exclude_files or []
    exclude_dir_list = exclude_dirs or []
    print("===", exclude_file_list)


    tocompile_file_list = []
    tocompile_cfile_list = []
    for search_ext in _tocompile_ext_list:
        search_glob_pattern = os.path.join(f"**{os.sep}*.{search_ext}")
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
            path_and_purename, ext = os.path.splitext(filepath)
            c_filepath = f"{path_and_purename}.c"

            tocompile_cfile_list.append(c_filepath)
    
    os.chdir(orig_cwd)
    return tocompile_file_list, tocompile_cfile_list

