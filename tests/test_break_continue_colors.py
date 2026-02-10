
from serpent.core import generate_graphviz_flowchart
from serpent.resources import THEMES

def test_break_continue_colors():
    """
    Verify that break and continue nodes get their specific colors 
    from the theme configuration.
    """
    import textwrap
    code = textwrap.dedent("""
    while True:
        if condition:
            break
        else:
            continue
    """)
    
    # Use Classic theme which has specific colors for break/continue
    theme = THEMES["Classic (Pastel)"]
    break_color = theme["break"]      # mistyrose
    continue_color = theme["continue"] # lightgray

    
    graph = generate_graphviz_flowchart(code, style_config=theme)
    dot_source = graph.source
    
    print("Checking for break color:", break_color)
    if f'fillcolor="{break_color}"' in dot_source or f'fillcolor={break_color}' in dot_source:
        print("PASS: Break node has correct color.")
    else:
        print(f"FAIL: Break node missing color {break_color}")
        raise AssertionError("Break node styling failed")

    print("Checking for continue color:", continue_color)
    if f'fillcolor="{continue_color}"' in dot_source or f'fillcolor={continue_color}' in dot_source:
        print("PASS: Continue node has correct color.")
    else:
        print(f"FAIL: Continue node missing color {continue_color}")
        raise AssertionError("Continue node styling failed")

if __name__ == "__main__":
    test_break_continue_colors()
