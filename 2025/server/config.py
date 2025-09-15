"""
Aedificium server config
"""

import os


def env_to_bool(env):
    """
    Convert an environment variable value to a boolean
    """
    return env.lower() in ("true", "1")


DEBUG = env_to_bool(os.environ.get("DEBUG", "False"))

if DEBUG:
    DATABASE_CONFIG = dict(
        url="sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
else:
    DATABASE_CONFIG = dict(
        url="sqlite:////data/aedificium.db",
        connect_args={"check_same_thread": False},
    )
