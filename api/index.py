import os
import sys

root_dir = os.path.dirname(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, 'backend')
sys.path.insert(0, root_dir)
sys.path.insert(0, backend_dir)

# Vercel needs to see 'app' imported directly at the top level
from backend.app.main import app
