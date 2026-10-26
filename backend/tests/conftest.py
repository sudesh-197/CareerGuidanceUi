"""
Shared pytest setup.

* puts ``backend/`` on ``sys.path`` so ``import app`` works from any working directory
* points the app at a throw-away SQLite file, so the tests (several of which create
  users, posts, ...) can never touch the real ``career_guidance.db``

Run from the backend folder:  python -m pytest tests -q
"""

import os
import sys
import tempfile

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

_tmp_db = os.path.join(tempfile.mkdtemp(prefix='careerai_tests_'), 'test.db')
os.environ.setdefault('DATABASE_URL', f'sqlite:///{_tmp_db}')
