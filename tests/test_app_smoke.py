"""
Smoke tests for the Streamlit application.
"""
from streamlit.testing.v1 import AppTest
from serpent import app

def test_app_startup():
    """
    Smoke test to verify the app starts up without errors.
    """
    at = AppTest.from_file(app.__file__).run()
    
    # Check if the caption is correct (title is conditional on banner presence)
    assert at.caption[0].value == "Turn your Python functions into clear, standard flowcharts in a few clicks."
    assert not at.exception
