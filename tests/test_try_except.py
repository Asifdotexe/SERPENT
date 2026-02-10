from serpent.core import generate_graphviz_flowchart


def test_try_except_structure():
    """Test that try/except blocks are correctly structured."""
    code = """
try:
    process()
except ValueError:
    handle_error()
else:
    success()
finally:
    cleanup()
"""
    graph = generate_graphviz_flowchart(code)
    source = graph.source

    # Check for nodes
    assert "label=Try" in source
    assert "label=Attempt" in source
    assert "Exc: ValueError" in source

    # Check content
    assert "process" in source
    assert "handle_error" in source
    assert "success" in source
    assert "cleanup" in source
