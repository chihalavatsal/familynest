import os
import sys

# Add the root directory to sys.path so 'backend' can be resolved
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app.main import app
