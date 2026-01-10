"""
Core logic for parsing Python code with AST and drawing a flowchart.

It leverages Python's Abstract Syntax Tree (AST) to traverse code structure and `graphviz`
to generate visual flowcharts.
"""

import ast
from typing import Any, Optional, Union

from graphviz import Digraph


class PythonFlowchartGV(ast.NodeVisitor):
    """
    Custom AST NodeVisitor that generates Graphviz Digraph representing the control flow of Python code

    This class walks through the Python code structure (AST) and converts it into a visual graph.
    Instead of boring old stack, we use a smarter `last_nodes` list to keep track of connections.
    """

    def __init__(self) -> None:
        """
        Initialize the Flowchart Visitor.

        We need to setup the blank canvas (Digraph) where we will draw our shapes.
        Also need some counters and lists to remember where we came from,
        so we know where to go next.
        """
        self.graph: Digraph = Digraph(format="png")
        self.counter: int = 0

        # Why last_nodes?
        # Imagine you are walking in a park. You need to know where you are standing right now
        # to know where you can walk to next. This list keeps track of the ID of the nodes
        # that are waiting to be connected to the next instruction.
        # Initially empty because we haven't started walking yet!
        self.last_nodes: list[Union[str, tuple[str, Optional[str]]]] = []

        # Why loop_stack?
        # Loops are tricky, bhai.
        # Sometimes you want to `break` out (exit) or `continue` (go back start).
        # We need to remember which loop we are currently inside so we know where to jump to.
        # It's like inception - loop inside loop inside loop.
        self.loop_stack: list[dict[str, Any]] = []

    def new_node(
        self,
        label: str,
        shape: str = "box",
        connect_from: Optional[list[Union[str, tuple[str, Optional[str]]]]] = None,
        edge_label: str = "",
    ) -> str:
        """
        Create a new node in the flowchart and connect it to previous nodes.

        This is the main painter! It takes a command, makes a shape, and draws lines (edges)
        from the previous steps to this new step. It handles all the coloring and labeling too.

        :param label: The text to display inside the box/diamond/circle.
        :param shape: The geometric shape of the node (box, diamond, oval, etc.).
        :param connect_from: Specific list of nodes to connect FROM. If None, uses the last visited nodes.
        :param edge_label: Text to write on the arrow connecting to this new node (e.g., "True", "False").
        :return: The unique ID of the newly created node (like "n1", "n2").
        """
        # Global override check
        # Checking if some previous logic left a note saying "Hey, the next edge needs this label!"
        override_label = getattr(self, "next_edge_label", None)
        if override_label:
            edge_label = override_label
            # Used it, now forget it.
            self.next_edge_label = None

        # FIXME: Make these enumerations
        # Making it look pretty with pastel colors.
        # Life is too short for boring black and white charts, na?
        color_map = {
            "box": "lightyellow",
            "diamond": "lightblue",
            "oval": "lightgreen",
            "circle": "thistle",
            "parallelogram": "lightcyan",
        }
        fillcolor = color_map.get(shape, "white")

        node_id = f"n{self.counter}"
        self.counter += 1

        self.graph.node(
            node_id, label=label, shape=shape, style="filled", fillcolor=fillcolor
        )

        # Deciding who is the parent of this new node.
        # Default is `self.last_nodes` (the immediate previous steps).
        sources = connect_from if connect_from is not None else self.last_nodes

        for source in sources:
            src_id = source
            lbl = edge_label

            # If the source is complex (tuple), it might carry its own specific label instruction.
            # Example: An `If` node sends "True" to one guy and "False" to another.
            if isinstance(source, tuple):
                src_id = source[0]
                if source[1]:  # If specific label exists, it wins!
                    lbl = source[1]

            self.graph.edge(src_id, node_id, label=lbl)

        # Update current state: This new node is now the "last node".
        self.last_nodes = [node_id]
        return node_id

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Handle function definition.

        :param node: The AST node for the function.
        """
        name = node.name
        start_node = self.new_node(f"Function: {name}", shape="oval")

        # Function body starts here.
        self.last_nodes = [start_node]

        # Go inside the function and visit every line of code.
        for stmt in node.body:
            self.visit(stmt)

        # Function over! We don't explicitly add "End" node, flow just stops.

    def visit_If(self, node: ast.If) -> None:
        """
        Handle `if` statements.

        Life is full of choices, and so is code. We create a diamond shape for the decision.
        Then we split the path: one way for YES (True), one way for NO (False).
        Finally, we have to bring them back together (merge) because the code eventually moves on.

        :param node: The AST node for the if statement.
        """
        condition_label = f"If: {ast.unparse(node.test)}"
        decision_node = self.new_node(condition_label, shape="diamond")

        decision_node_id = decision_node

        # Condition is "True"
        # We prepare to visit the lines inside the `if` block.
        # We cheat a bit and set a global flag so the first node inside gets connected with "True" label.
        self.last_nodes = [decision_node_id]
        true_end_nodes = []

        if node.body:
            self.next_edge_label = "True"
            self.last_nodes = [decision_node_id]
            for stmt in node.body:
                self.visit(stmt)
            true_end_nodes = self.last_nodes
        else:
            # Empty body? Just pass through.
            true_end_nodes = [decision_node_id]

        # Condition is "False"
        false_end_nodes = []
        if node.orelse:
            self.next_edge_label = "False"
            self.last_nodes = [decision_node_id]
            for stmt in node.orelse:
                self.visit(stmt)
            false_end_nodes = self.last_nodes
        else:
            # If there is no else, the False path goes straight from decision to the merge point.
            # We explicitly label this edge as "False".
            false_end_nodes = [(decision_node_id, "False")]

        # Decision merge (Joining of the splits)
        # We collect all the endpoints from True path and False path.
        # The next line of code after this big IF will connect from ALL of these endpoints.
        start_merge_nodes = []
        for n in true_end_nodes:
            if isinstance(n, tuple):
                start_merge_nodes.append(n)
            else:
                start_merge_nodes.append((n, None))

        for n in false_end_nodes:
            if isinstance(n, tuple):
                start_merge_nodes.append(n)
            else:
                start_merge_nodes.append((n, None))

        self.last_nodes = start_merge_nodes
        # Cleanup
        self.next_edge_label = None

    def visit_For(self, node: ast.For) -> None:
        """Handle `for` loops using common loop logic.

        :param node: The loop node.
        """
        return self._handle_loop(
            node, f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}"
        )

    def visit_While(self, node: ast.While) -> None:
        """Handle `while` loops using common loop logic.

        :param node: The loop node.
        """
        return self._handle_loop(node, f"While: {ast.unparse(node.test)}")

    def _handle_loop(self, node: Union[ast.For, ast.While], label: str) -> None:
        """
        Common logic for processing loops.

        Loops are circles of life.
        1. Enter the circle (Condition).
        2. Do the work (Body).
        3. Go back to start (Back-edge).
        4. Or leave if done (Exit).
        Also handles those rebellious `break` and `continue` statements.

        :param node: The loop node.
        :param label: Label for the condition node.
        """
        # The Gatekeeper (Condition Node)
        # Using diamond because it is a decision point (True/False).
        condition_node = self.new_node(label, shape="diamond")

        # We push a new context to the stack so `break` and `continue` know who their daddy is (current loop).
        self.loop_stack.append(
            {"break": [], "continue": [], "start_node": condition_node}
        )

        # Doing the work (Body - True Path)
        self.next_edge_label = "True"
        self.last_nodes = [condition_node]

        for stmt in node.body:
            self.visit(stmt)

        # The Return Logic (Back-edge)
        # Everyone who reached the end of the body must go back to the condition to check again.
        for n in self.last_nodes:
            src = n[0] if isinstance(n, tuple) else n
            lbl = n[1] if isinstance(n, tuple) else None
            self.graph.edge(src, condition_node, label=lbl)

        # Handling `continue` (Shortcuts)
        # Any `continue` we found inside just jumps straight back to condition.
        loop_ctx = self.loop_stack.pop()
        for cont_node in loop_ctx["continue"]:
            self.graph.edge(cont_node, condition_node)

        # The Exit Strategy
        # The next code connects from:
        # - The condition (when it becomes False).
        # - Any `break` statements (they escape the loop).
        exit_nodes = [(condition_node, "False")]
        for break_node in loop_ctx["break"]:
            exit_nodes.append((break_node, None))

        self.last_nodes = exit_nodes
        self.next_edge_label = None

    def visit_Break(self, node: ast.Break) -> None:
        """
        Handle `break` statement.

        Emergency exit! We cut the current flow and register this node in the
        `break` list of the parent loop. It will be re-connected later to the exit.
        """
        if self.loop_stack:
            break_node = self.new_node("break", shape="box")
            self.loop_stack[-1]["break"].append(break_node)
            # Dead end here, flow transfers to loop exit.
            self.last_nodes = []
        else:
            self.new_node("break (orphaned)", shape="box")

    def visit_Continue(self, node: ast.Continue) -> None:
        """
        Handle `continue` statement.

        Skip the rest, go back to start! We register this in `continue` list
        and cut the local flow.
        """
        if self.loop_stack:
            cont_node = self.new_node("continue", shape="box")
            self.loop_stack[-1]["continue"].append(cont_node)
            self.last_nodes = []
        else:
            self.new_node("continue (orphaned)", shape="box")

    def visit_Return(self, node: ast.Return) -> None:
        """
        Handle `return` statement.

        Game over for this function. We return the value and stop the flow here.
        """
        val = ast.unparse(node.value) if node.value else "None"
        self.new_node(f"Return: {val}", shape="box")
        self.last_nodes = []

    def visit_Expr(self, node: ast.Expr) -> None:
        """Handle expression statements (ignoring docstrings).

        :param node: The expression node to handle.
        """
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            # Skip docstrings, they are for reading not flowcharting.
            return
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle variable assignment.

        :param node: The assignment node to handle.
        """
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Handle augmented assignment (+=, -= etc).

        :param node: The augmented assignment node to handle.
        """
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Handle annotated assignment (x: int = 5).

        :param node: The annotated assignment node to handle.
        """
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_Pass(self, node: ast.Pass) -> None:
        """
        Handle `pass`.

        Do nothing. Chill. The flow continues as if nothing happened.

        :param node: The pass node to handle.
        """
        pass

    def generic_visit(self, node: ast.AST) -> None:
        """Fallback for any other node types.

        :param node: The node to handle.
        """
        if isinstance(node, ast.stmt):
            self.new_node(f"{type(node).__name__}", shape="box")
        else:
            super().generic_visit(node)


def generate_graphviz_flowchart(code_str: str, title: str = "Flowchart") -> Digraph:
    """
    Parse Python source code and generate a Graphviz Digraph.

    This is the wrapper function that the outside world calls.
    It catches syntax errors so the app doesn't crash on bad code.

    :param code_str: The raw Python code string to parse.
    :param title: The title to display on the flowchart.
    :returns: The generated Graphviz object ready to rendering.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        # If the user types garbage, we show a nice error box instead of crashing.
        graph = Digraph()
        graph.node(
            "error",
            label="Syntax Error: Cannot parse code",
            shape="box",
            style="filled",
            fillcolor="lightpink",
        )
        return graph

    fc = PythonFlowchartGV()
    fc.visit(tree)
    fc.graph.attr(label=title, labelloc="t", fontsize="20")
    return fc.graph
