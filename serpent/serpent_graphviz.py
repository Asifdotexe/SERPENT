"""
Core logic for parsing Python code with AST and drawing a flowchart.

It leverages Python's Abstract Syntax Tree (AST) to traverse code structure and `graphviz`
to generate visual flowcharts.
"""

import ast
from graphviz import Digraph


class PythonFlowchartGV(ast.NodeVisitor):
    """A custom AST NodeVisitor that generates a Graphviz Digraph representing the control flow of Python code.

    :ivar graph: The `graphviz.Digraph` object where the flowchart is built.
    :ivar counter: A counter used to generate unique IDs for graph nodes.
    :ivar stack: A list acting as a stack to keep track of the last node in the
                 current flow path. This is crucial for connecting subsequent nodes.
    """

    def __init__(self):
        """Initialize the flowchart visitor with a new Graphviz directed graph, a unique node counter,
        and an empty stack for tracking control flow.
        """
        self.graph = Digraph(format='png')
        self.counter = 0
        self.stack = []

    def new_node(self, label: str, shape: str = "box") -> str:
        """Create a new node in the Graphviz flowchart with a specified label and shape,
        connect it to the previous node in the current flow path, and return its unique ID.

        :param label: The text to display inside the node.
        :param shape: The shape of the node (e.g., "box", "diamond", "oval", "circle"), defaults to "box"
        :return: The unique identifier of the newly created node.
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
        self.graph.node(name, label=label, shape=shape,
                        style="filled", fillcolor=fillcolor)

        # Connect this new node from the last node on the stack,
        # establishing the sequential flow of the flowchart.
        if self.stack:
            self.graph.edge(self.stack[-1], name)

        # Make this new node the latest point in the current flow path.
        self.stack.append(name)
        return name

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handles a function definition node by creating an oval node for the function entry and visiting its body.

        Creates a flowchart node representing the function, traverses its statements,
        and updates the flow stack to resume the parent scope after processing.

        :param node: The AST node representing the Function defination.
        """
        self.new_node(f"Function: {node.name}", "oval")

        # Visit all statements inside the function's body to build its internal flow.
        self.generic_visit(node)

        # After the function body, remove its last node from the stack.
        # This signifies that the main flow continues from the point before the function definition.
        self.stack.pop()

    def visit_If(self, node: ast.If) -> None:
        """Visit an `ast.If` node and add a decision node with branching for the if/else structure in the flowchart.
        Creates a diamond-shaped node for the condition, processes both true and false branches
        so their flows originate from the decision node, and merges the flow at the end of the branches
        to maintain correct control flow in the graph.

        :param node: The AST node representing the If loop.
        """
        cond = self.new_node(f"If: {ast.unparse(node.test)}", "diamond")

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

    def visit_For(self, node: ast.For) -> None:
        """Handles a for loop node by adding a circular node for the loop and connecting its body to the flowchart.

        :param node: The AST node representing the for loop.
        """
        self.new_node(
            f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}",
            "circle"
        )

        # Visit all statements inside the loop's body.
        self.generic_visit(node)

        # After the loop body, remove its last node from the stack.
        # This signifies that the main flow continues from the point before the loop's body.
        self.stack.pop()

    def visit_While(self, node: ast.While) -> None:
        """Visit a while loop node and add its control flow to the graph.
        Creates a circular node labeled with the loop condition, processes the loop body,
        and updates the flowchart to reflect the loop's structure.

        :param node: The AST node representing the While loop.
        """
        self.new_node(f"While: {ast.unparse(node.test)}", "circle")

        # Visit all statements inside the loop's body.
        self.generic_visit(node)

        # Remove the last node of the loop body from the stack.
        self.stack.pop()

    def visit_Expr(self, node: ast.Expr) -> None:
        """Visit an expression statement node and add it as a box-shaped node to the flowchart,
        excluding standalone string literals such as docstrings.

        :param node: The AST node representing the Expression statment.
        """
        # Ignore standalone string literals (often docstrings) as flowchart nodes.
        if isinstance(node.value, (ast.Str, ast.Constant)) \
                and isinstance(node.value.value, str):
            return

        self.new_node(ast.unparse(node).strip(), "box")

        # Remove the last node from the stack. For simple expressions, once processed,
        # their specific role in maintaining the flow sequence on the stack is complete.
        self.stack.pop()

    def visit_Return(self, node: ast.Return) -> None:
        """Handle a return statement by adding a box-shaped node labeled with the return expression
        and updating the flow to reflect termination of the current path.

        :param node: The AST node representing the Return statement.
        """
        self.new_node(f"Return: {ast.unparse(node.value)}", "box")

        # Remove the last node from the stack. A 'return' statement often signifies
        # the termination of a flow path, so the stack needs to reflect the prior state.
        self.stack.pop()


def generate_graphviz_flowchart(code_str: str, title: str = "Flowchart") -> Digraph:
    """Parse Python source code and generate a Graphviz Digraph visualizing its control flow as a flowchart.

    :param code_str: Python source code to visualize.
    :param title: Title displayed at the top of the flowchart, defaults to "Flowchart"
    :return: A Graphviz Digraph object representing the code's control flow.
    """
    tree = ast.parse(code_str)
    fc = PythonFlowchartGV()
    fc.visit(tree)
    fc.graph.attr(label=title, labelloc="t", fontsize="20")
    return fc.graph
