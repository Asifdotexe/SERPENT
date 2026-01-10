
from serpent.core import generate_graphviz_flowchart

code = """
while x > 0:
    print(x)
    x -= 1
"""

graph = generate_graphviz_flowchart(code)
print(graph.source)
