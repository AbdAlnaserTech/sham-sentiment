"""Launch the Streamlit application."""

import subprocess
import sys
import os


def main() -> None:
    app_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "main.py")
    cmd = [sys.executable, "-m", "streamlit", "run", app_main]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
