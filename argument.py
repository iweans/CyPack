import argparse
# ------------------------------
# ----------------------------------------


def parse_args() -> argparse.Namespace:
    args_parser = argparse.ArgumentParser(
        description="将指定路径项目进行编译打包",

    )
    args_parser.format_usage()

    args_parser.add_argument("src", help="Source directory project in.",
                             default="")
    args_parser.add_argument("-dst", help="Destination directory packaging to.",
                             default="")
    args = args_parser.parse_args()


    print("src =", args.src)
    print("dst =", args.dst)

    print(type(args))
    return args
