import os


def get_app_root_dir() -> str:
    """
    Returns the full path of the application repository.
    """
    util_dir = os.path.dirname(__file__)
    atat_src_dir = os.path.dirname(util_dir)
    git_root_dir = os.path.dirname(atat_src_dir)

    return git_root_dir


def get_path_from_root(filename: str) -> str:
    return os.path.join(get_app_root_dir(), filename)
