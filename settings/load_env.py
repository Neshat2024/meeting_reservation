# import os
# from pathlib import Path
#
# from dotenv import load_dotenv
#
# BASE_DIR = Path(__file__).resolve().parent.parent
#
#
# def load_env_variables(env_name):
#     env_path = f"{BASE_DIR}/{env_name}"
#     load_dotenv(env_path)
#     return {key: os.getenv(key) for key in os.environ if key in open(env_path).read()}
import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_variables(env_name: str = ".env") -> Dict[str, str]:
    """Load environment variables from specified file.

    Args:
        env_name: Name of the .env file (e.g., ".env.instance1")

    Returns:
        Dictionary of loaded environment variables
    """
    env_path = BASE_DIR / env_name
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file {env_path} not found")

    load_dotenv(env_path, override=True)

    # Read all variables from the .env file
    with open(env_path) as f:
        env_lines = f.readlines()

    # Extract variable names (lines that look like VAR=value)
    var_names = [
        line.split("=")[0].strip()
        for line in env_lines
        if line.strip() and not line.startswith("#") and "=" in line
    ]

    # Return only variables that were defined in the .env file
    return {key: os.getenv(key) for key in var_names if os.getenv(key) is not None}
