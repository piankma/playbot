from os import path
from sys import exit
from glob import glob
from yaml import load, loader, error

config_dir = path.abspath(path.join(path.curdir, "config"))


def load_config():
    result = dict()

    for f in _get_config_file_list():
        with open(f, "r") as stream:
            name, ext = path.splitext(path.basename(f))
            try:
                result[name] = load(stream, Loader=loader.SafeLoader)
            except error.YAMLError as exc:
                print("YAML loading error:\n")
                print(exc)
                exit(78)  # EX_CONFIG, see `man sysexits`

    return result


def _get_config_file_list():
    for f in glob(f"{config_dir}/*.yaml"):
        yield path.join(config_dir, f)
