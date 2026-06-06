"""Initialize SQLite database and default users."""

import sys
import os

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

from db.database import init_database  # noqa: E402
from db.repository import ensure_default_users  # noqa: E402
from paths import ProjectPaths  # noqa: E402

if __name__ == "__main__":
    paths = ProjectPaths.from_project_root(bootstrap.ROOT)
    db = init_database(paths.db_path)
    ensure_default_users()
    print(f"Database ready: {db}")
    print("Demo users: admin / Admin@2026 | analyst / Analyst@2026")
