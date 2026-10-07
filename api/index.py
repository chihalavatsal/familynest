import os
import sys

# Add the root directory AND the backend directory to sys.path
root_dir = os.path.dirname(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, 'backend')
sys.path.insert(0, root_dir)
sys.path.insert(0, backend_dir)

from backend.app.main import app
