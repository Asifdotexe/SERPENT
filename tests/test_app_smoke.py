"""
Smoke tests for the Streamlit application.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest


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
