import os
import json


def parse_pkg_cfg(target_project_dir):

    pkg_cfg_path = os.path.join(target_project_dir, "pkg_cfg.json")

    with open(pkg_cfg_path, "r") as f:
        pkg_cfg = json.loads(f.read())

    return pkg_cfg
