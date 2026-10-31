import os
import subprocess
import sys
from pathlib import Path


def _relaunch_in_project_venv():
    """Re-run this script with the project's virtual environment, if it exists."""
    root = Path(__file__).resolve().parent
    candidates = (root / ".venv" / "Scripts" / "python.exe", root / ".venv" / "bin" / "python")
    for python in candidates:
        if python.is_file() and Path(sys.executable).resolve() != python.resolve():
            raise SystemExit(subprocess.call([str(python), *sys.argv]))
    return False


try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    if __name__ == "__main__" and os.environ.get("SMS_VENV_RELAUNCHED") != "1":
        os.environ["SMS_VENV_RELAUNCHED"] = "1"
        _relaunch_in_project_venv()
    raise

load_dotenv(Path(__file__).resolve().with_name(".env"))

from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=app.debug)
