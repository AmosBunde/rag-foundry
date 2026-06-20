import os
import sys

# Add the backend directory to the path so `import app` resolves correctly.
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))
