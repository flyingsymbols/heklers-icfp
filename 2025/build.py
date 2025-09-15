#!/usr/bin/env python3

"""
Build script for aedificium server
"""

import argparse
import os
import subprocess

REPO_PATH = (
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
)
AEDIFICIUM_PATH = os.path.join(REPO_PATH, "2025")
SERVER_PATH = os.path.join(AEDIFICIUM_PATH, "server")

SERVER_IMAGE_NAME = "aedificium"

BUILD_TYPES = {
    "server": "Build the server image",
}


def build_server(debug=False, run=False, run_port=80):
    """
    Build the aedificium server and optionally run it (on port 80)
    """
    subprocess.check_call(
        ["docker", "build", ".", "-f", "./docker/Dockerfile", "-t", SERVER_IMAGE_NAME],
        cwd=AEDIFICIUM_PATH,
    )

    if run:
        opts = []
        if debug:
            opts.extend(["-e", f"DEBUG={debug}"])
        else:
            opts.extend(["-v", "aedificium_data:/data"])
        if run_port:
            opts.extend(["-p", f"{run_port}:8000"])
        else:
            opts.extend(["-p", "8000"])
        try:
            subprocess.check_call(["docker", "run", "-it", *opts, SERVER_IMAGE_NAME])
        except KeyboardInterrupt:
            pass


def cli():
    """
    CLI for builds
    """
    root_parser = argparse.ArgumentParser(
        description="Build script for aedificium server",
    )
    subparsers = root_parser.add_subparsers(
        title="Choose a build type",
        dest="build_type",
        required=True,
        metavar="<build_type>",
    )

    # add the build types
    for build_type, description in BUILD_TYPES.items():
        parser = subparsers.add_parser(build_type, help=description)

        # add any per-build options
        if build_type == "server":
            parser.add_argument("--debug", action="store_true")
            parser.add_argument(
                "--run", action="store_true", help="Run the server after build"
            )
            parser.add_argument(
                "--run-port",
                action="store",
                default=80,
                help="Specify the port to use for the server",
            )

    args = root_parser.parse_args()

    # run the chosen build
    if args.build_type == "server":
        build_server(args.debug, args.run, args.run_port)


if __name__ == "__main__":
    cli()
