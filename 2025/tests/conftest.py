

import sys
import os
import subprocess

REPO_PATH = (
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
)

AEDIFICIUM_PATH = os.path.join(REPO_PATH, "2025")

sys.path.insert(0, AEDIFICIUM_PATH)
