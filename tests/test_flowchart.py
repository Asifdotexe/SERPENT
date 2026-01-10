
import pytest
from serpent.graphviz import generate_graphviz_flowchart

def test_simple_function():
    """
    Test a simple linear function.
    """
    code = """
def hello():
    print("Hello")
    return True
"""
    graph = generate_graphviz_flowchart(code)
    source = graph.source
    assert "Function: hello" in source
    assert "print" in source
    assert "Return" in source

def test_if_else():
    """
    Test if/else branching logic.
    """
    code = """
if x > 5:
    a = 1
else:
    a = 2
"""
    graph = generate_graphviz_flowchart(code)
    source = graph.source
    # Check for diamond (condition)
    assert "If: x > 5" in source
    assert 'shape=diamond' in source
    # Check for True/False edges
    assert 'label=True' in source
    assert 'label=False' in source

def test_loop_with_break():
    """
    Test loop handling with break statement.
    """
    code = """
while True:
    if x:
        break
    print("Looping")
"""
    graph = generate_graphviz_flowchart(code)
    source = graph.source
    assert "While: True" in source
    assert "break" in source
    # We can't easily check edge connectivity via regex on DOT, 
    # but presence of nodes is a good start.

def test_invalid_syntax():
    """
    Test that invalid syntax returns an error node.
    """
    code = "def broken_code(: ..."
    graph = generate_graphviz_flowchart(code)
    assert "Syntax Error" in graph.source
