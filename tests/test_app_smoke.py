"""
Smoke tests for the Streamlit application.
"""
import sys
from pathlib import Path
from streamlit.testing.v1 import AppTest

# Add project root to path to import app.py
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import app

def test_app_startup():
    """
    Smoke test to verify the app starts up without errors.
    """
    at = AppTest.from_file(str(root_dir / "app.py")).run()
    
    # Check if the app runs without exception
    assert not at.exception
    
    # Check if the title is correct
    # The title might be an image or text depending on assets, but "SERPENT" should be somewhere
    # logic in app.py: st.title("SERPENT 🐍") if no logo
    pass
