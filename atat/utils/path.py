"""
Helpers for handling getting the path of the ATAT application and resources.
"""

import os


def get_app_root_dir() -> str:
    """
    Returns the full path of the application repository.

    Note that this is not the root of the Python project but the root of the git/code
    repository. This ensures that the other resources can be loaded.

    :returns: The root of the ATAT code repository
    """

    # Maintenance note: If this code moves to another module of if this module is moved to
    # another package, this code will need to be updated as it is rather fragile in that
    # regard. __file__ is the path to this module, which is within atat/util, so the root of the
    # repository is 3 "dirname" calls "up".
    # This also would break if we used a tool like PyInstaller or PyOxidizer, which "freeze" the
    # application and can "break" __file__ from being what we expect.
    # This is more reliable; however, than relying on cwd() since we don't necessarily know which
    # directoy the application is being run from.

    util_dir = os.path.dirname(__file__)
    atat_src_dir = os.path.dirname(util_dir)
    git_root_dir = os.path.dirname(atat_src_dir)

    return git_root_dir


def get_path_from_root(filename: str) -> str:
    """
    Get the path to a file, relative to the root of the project.

    :param str filename: The relative path from the root of the resource to load
    :returns: The absolute path to the given file name
    """

    return os.path.join(get_app_root_dir(), filename)
