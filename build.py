import os
import shutil
import subprocess
from argparse import ArgumentParser


def configure(version, build_dir):
    autodesk_dir = os.environ.get("MAYA_LOCATION", "C:/Program Files/Autodesk")
    print(autodesk_dir)
    if not os.path.isdir(autodesk_dir):
        raise ValueError("Invalid Autodesk directory: {0}".format(autodesk_dir))
    cmake = subprocess.run(['cmake',
                            '.',
                            '-B',
                            build_dir,
                            f'-DMAYA_LOCATION={autodesk_dir}',
                            f'-DMAYA_VERSION={version}'])
    return cmake.returncode


def build(*args):
    # Parse arguments
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--ver", default=2020, type=int, help="Maya version")
    args = arg_parser.parse_args(*args)

    # Setup directory and configure
    build_dir = f"./build/{args.ver}"
    if os.path.isdir(build_dir):
        print("Removing old build...")
        shutil.rmtree(build_dir)
    err = configure(args.ver, build_dir)
    if err:
        return

    # Cmake build
    print(f"Building for Maya {args.ver}...")
    cmake_build = subprocess.run(['cmake', '--build', build_dir])
    return cmake_build.returncode


if __name__ == "__main__":
    build(os.sys.argv[1:])
