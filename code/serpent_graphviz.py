"""
Core logic for parsing Python code with AST and drawing a flowchart.

It leverages Python's Abstract Syntax Tree (AST) to traverse code structure and `graphviz`
to generate visual flowcharts.
"""

import ast
from graphviz import Digraph


class PythonFlowchartGV(ast.NodeVisitor):
    """
    A custom AST NodeVisitor that generates a Graphviz Digraph representing
    the control flow of Python code.

    :ivar graph: The `graphviz.Digraph` object where the flowchart is built.
    :ivar counter: A counter used to generate unique IDs for graph nodes.
    :ivar stack: A list acting as a stack to keep track of the last node in the
                 current flow path. This is crucial for connecting subsequent nodes.
    """

    def __init__(self):
        """
        Initializes the Flowchart Graphviz Visitor.
        """
        self.graph = Digraph(format='png')
        self.counter = 0
        self.stack = []

    def new_node(self, label: str, shape: str = "box") -> str:
        """
        Creates a new node in the Graphviz graph and handles its connection
        to the previous node in the current flow path based on the internal stack.

        :param label: The text label to display inside the node.
        :type label: str
        :param shape: The shape of the node (e.g., "box", "diamond", "oval").
                      Defaults to "box".
        :type shape: str
        :returns: The unique name (ID) of the newly created node.
        :rtype: str
        """

        # Assign light pastel colors based on shape
        color_map = {
            "box": "lightyellow",
            "diamond": "lightblue",
            "oval": "lightgreen",
            "circle": "thistle"
        }

        fillcolor = color_map.get(shape, "white")

        name = f"n{self.counter}"
        self.counter += 1
        self.graph.node(name, label=label, shape=shape, style="filled", fillcolor=fillcolor)

        # Connect this new node from the last node on the stack,
        # establishing the sequential flow of the flowchart.
        if self.stack:
            self.graph.edge(self.stack[-1], name)

        # Make this new node the latest point in the current flow path.
        self.stack.append(name)
        return name

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visits an `ast.FunctionDef` node (function definition).

        This method creates an oval-shaped node for the function's entry point,
        then recursively visits its body. After the body is processed, it pops
        the last node of the function's flow from the stack, signaling a return
        to the parent scope's flow.

        :param node: The `ast.FunctionDef` node being visited.
        :type node: ast.FunctionDef
        """
        self.new_node(f"Function: {node.name}", "oval")

        # Visit all statements inside the function's body to build its internal flow.
        self.generic_visit(node)

        # After the function body, remove its last node from the stack.
        # This signifies that the main flow continues from the point before the function definition.
        self.stack.pop()

    def visit_If(self, node: ast.If):
        """
        Visits an `ast.If` node (if/elif/else conditional statement).
        This method handles the branching logic of 'if' statements by:
        1. Creating a diamond-shaped decision node.
        2. Temporarily resetting the stack for the 'true' and 'false' branches
           to ensure their paths originate correctly from the decision node.
        3. Capturing the end nodes of each branch.
        4. Setting the stack to the appropriate branch end to implicitly merge the flow.

        :param node: The `ast.If` node being visited.
        """
        cond = self.new_node(f"If: {ast.unparse(node.test)}", "diamond")

        # 'cond' is now on top of the stack. 'parent' points to the node
        # that was the last in the main flow *before* the 'if' condition was added.
        parent = self.stack[-1]

        # === True branch ===
        # Reset the stack to start this branch from the 'cond' (diamond) node,
        # effectively creating a new path originating from the decision point.
        self.stack = [cond]

        # Process all statements in the 'if' body (the 'true' block).
        for stmt in node.body:
            self.visit(stmt)

        # Capture the last node of the true path. This will be used for implicit merging.
        true_end = self.stack[-1]

        # === False branch ===
        if node.orelse:
            # If an 'else' block exists, reset the stack again. This prepares for
            # processing the 'false' path, ensuring it also originates directly from the 'cond' node.
            self.stack = [cond]

            # Process all statements in the 'else' body (the 'false' block).
            for stmt in node.orelse:
                self.visit(stmt)

            # Capture the last node of the false path.
            false_end = self.stack[-1]

            # After both branches, set the stack to the end of the false branch.
            # This implicitly merges the flow, meaning any subsequent statements
            # after the entire if-else structure will connect from the end of the 'else' block.
            self.stack = [false_end]
        else:
            # If there is NO 'else' block, the 'false' path effectively bypasses the 'if' body.
            # In this scenario, the flowchart's execution naturally continues from the end of
            # the 'true' branch (or the 'cond' node itself if the true body was empty).
            # We set the stack to `true_end` for correct subsequent connections.
            self.stack = [true_end]

    def visit_For(self, node: ast.For):
        """
        Visits an `ast.For` node (for loop).
        This method creates a circular node for the loop, visits its body, and then
        pops the last node of the loop body from the stack to resume the parent flow.

        :param node: The `ast.For` node being visited.
        """
        self.new_node(f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}", "circle")

        # Visit all statements inside the loop's body.
        self.generic_visit(node)

        # After the loop body, remove its last node from the stack.
        # This signifies that the main flow continues from the point before the loop's body.
        self.stack.pop()

    def visit_While(self, node: ast.While):
        """
        Visits an `ast.While` node (while loop).

        Similar to `visit_For`, this creates a circular node for the loop,
        visits its body, and pops the last node of the loop body from the stack.

        :param node: The `ast.While` node being visited.
        :type node: ast.While
        """
        self.new_node(f"While: {ast.unparse(node.test)}", "circle")

        # Visit all statements inside the loop's body.
        self.generic_visit(node)

        # Remove the last node of the loop body from the stack.
        self.stack.pop()

    def visit_Expr(self, node: ast.Expr):
        """
        Visits an `ast.Expr` node (expression statement).
        This method creates a box-shaped node for the expression. It specifically
        filters out standalone string literals, which are typically docstrings
        and not intended to be flowchart nodes.

        :param node: The `ast.Expr` node being visited.
        """
        # Ignore standalone string literals (often docstrings) as flowchart nodes.
        if isinstance(node.value, (ast.Str, ast.Constant)) and isinstance(node.value.value, str):
            return

        self.new_node(ast.unparse(node).strip(), "box")

        # Remove the last node from the stack. For simple expressions, once processed,
        # their specific role in maintaining the flow sequence on the stack is complete.
        self.stack.pop()

    def visit_Return(self, node: ast.Return):
        """
        Visits an `ast.Return` node (return statement).
        This method creates a box-shaped node for the return statement.

        :param node: The `ast.Return` node being visited.
        """
        self.new_node(f"Return: {ast.unparse(node.value)}", "box")

        # Remove the last node from the stack. A 'return' statement often signifies
        # the termination of a flow path, so the stack needs to reflect the prior state.
        self.stack.pop()


def generate_graphviz_flowchart(code_str: str, title: str = "Flowchart") -> Digraph:
    """
    Parses Python source code and generates a Graphviz Digraph object
    representing its control flow as a flowchart.

    :param code_str: The Python source code as a string.
    :param title: The title to display at the top of the flowchart.
                  Defaults to "Flowchart".
    :returns: The configured `graphviz.Digraph` object, ready for rendering
              (e.g., to PNG, SVG).
    """
    tree = ast.parse(code_str)
    fc = PythonFlowchartGV()
    fc.visit(tree)
    fc.graph.attr(label=title, labelloc="t", fontsize="20")
    return fc.graph