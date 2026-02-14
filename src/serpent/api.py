"""
Public API for SERPENT.
"""
import inspect
from typing import Callable, Union, Optional, Any

from graphviz import Digraph
from serpent.core import generate_graphviz_flowchart


def serpentify(
    obj: Union[str, Callable],
    title: str = "Flowchart",
    **kwargs: Any
) -> Digraph:
    """
    Convert a Python function or code string into a flowchart.

    :param obj: The Python function or code string to convert.
    :param title: The title of the flowchart.
    :param kwargs: Additional arguments passed to the underlying generator.
                  Common arguments:
                  - rankdir: "TB" (Top-Bottom) or "LR" (Left-Right)
                  - style_config: A dictionary of style settings (see serpent.resources.THEMES)
    :return: A graphviz.Digraph object representing the flowchart.
    """
    if isinstance(obj, str):
        code_str = obj
    elif callable(obj):
        try:
            code_str = inspect.getsource(obj)
        except OSError as e:
            raise ValueError(
                f"Could not retrieve source code for {obj}. "
                "If it's defined in a REPL or interactive session, try passing the code as a string."
            ) from e
    else:
        raise TypeError(f"Expected a string or callable, got {type(obj)}")

    return generate_graphviz_flowchart(code_str, title=title, **kwargs)
