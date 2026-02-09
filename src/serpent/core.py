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
    A custom AST NodeVisitor that generates a Graphviz Digraph
    representing the control flow of Python code.
    """

    def __init__(
        self, rankdir: str = "TB", style_config: Optional[dict[str, str]] = None
    ) -> None:
        """
        Initialize the Flowchart Visitor.
        """
        self.graph: Digraph = Digraph(format="png")
        self.graph.attr(rankdir=rankdir)  # Set orientation (TB or LR)
        self.counter: int = 0
        self.last_nodes: list[Union[str, tuple[str, Optional[str]]]] = []
        self.loop_stack: list[dict[str, Any]] = []
        
        # Default colors if not provided
        self.style_config = style_config or {
            "box": "lightyellow",
            "diamond": "lightblue",
            "oval": "lightgreen",
            "circle": "thistle",
            "parallelogram": "lightcyan",
        }

    def new_node(
        self,
        label: str,
        shape: str = "box",
        connect_from: Optional[list[Union[str, tuple[str, Optional[str]]]]] = None,
        edge_label: str = "",
        node_type: Optional[str] = None,
    ) -> str:
        """
        Create a new node in the flowchart and connect it to previous nodes.
        """
        override_label = getattr(self, "next_edge_label", None)
        if override_label:
            edge_label = override_label
            self.next_edge_label = None

        fillcolor = self.style_config.get(node_type, self.style_config.get(shape, "white"))



        node_id = f"n{self.counter}"
        self.counter += 1

        self.graph.node(
            node_id, label=label, shape=shape, style="filled", fillcolor=fillcolor
        )

        sources = connect_from if connect_from is not None else self.last_nodes

        for source in sources:
            src_id = source
            lbl = edge_label

            if isinstance(source, tuple):
                src_id = source[0]
                if source[1]:
                    lbl = source[1]

            self.graph.edge(src_id, node_id, label=lbl)

        self.last_nodes = [node_id]
        return node_id

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handle function definition."""
        name = node.name
        start_node = self.new_node(f"Function: {name}", shape="oval")
        self.last_nodes = [start_node]
        for stmt in node.body:
            self.visit(stmt)

    def visit_If(self, node: ast.If) -> None:
        """Handle `if` statements."""
        condition_label = f"If: {ast.unparse(node.test)}"
        decision_node = self.new_node(condition_label, shape="diamond")
        decision_node_id = decision_node

        self.last_nodes = [decision_node_id]
        true_end_nodes = []

        if node.body:
            self.last_nodes = [(decision_node_id, "True")]
            for stmt in node.body:
                self.visit(stmt)
            true_end_nodes = self.last_nodes
        else:
            true_end_nodes = [(decision_node_id, "True")]

        false_end_nodes = []
        if node.orelse:
            self.last_nodes = [(decision_node_id, "False")]
            for stmt in node.orelse:
                self.visit(stmt)
            false_end_nodes = self.last_nodes
        else:
            false_end_nodes = [(decision_node_id, "False")]

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
        self.next_edge_label = None

    def visit_For(self, node: ast.For) -> None:
        """Handle `for` loops."""
        return self._handle_loop(
            node, f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}"
        )

    def visit_While(self, node: ast.While) -> None:
        """Handle `while` loops."""
        return self._handle_loop(node, f"While: {ast.unparse(node.test)}")

    def _handle_loop(self, node: Union[ast.For, ast.While], label: str) -> None:
        """Common logic for processing loops."""
        condition_node = self.new_node(label, shape="diamond")

        self.loop_stack.append(
            {"break": [], "continue": [], "start_node": condition_node}
        )

        self.last_nodes = [(condition_node, "True")]

        for stmt in node.body:
            self.visit(stmt)

        for n in self.last_nodes:
            src = n[0] if isinstance(n, tuple) else n
            lbl = n[1] if isinstance(n, tuple) else None
            if lbl:
                self.graph.edge(src, condition_node, label=lbl)
            else:
                self.graph.edge(src, condition_node)

        loop_ctx = self.loop_stack.pop()
        for cont_node in loop_ctx["continue"]:
            self.graph.edge(cont_node, condition_node)

        exit_nodes = [(condition_node, "False")]
        for break_node in loop_ctx["break"]:
            exit_nodes.append((break_node, None))

        self.last_nodes = exit_nodes
        self.next_edge_label = None

    def visit_Break(self, _node: ast.Break) -> None:
        """Handle `break` statement."""

        if self.loop_stack:
            break_node = self.new_node("break", shape="box", node_type="break")
            self.loop_stack[-1]["break"].append(break_node)
            self.last_nodes = []
        else:
            self.new_node("break (orphaned)", shape="box", node_type="break")

    def visit_Continue(self, _node: ast.Continue) -> None:
        """Handle `continue` statement."""
        if self.loop_stack:
            cont_node = self.new_node("continue", shape="box", node_type="continue")
            self.loop_stack[-1]["continue"].append(cont_node)
            self.last_nodes = []
        else:
            self.new_node("continue (orphaned)", shape="box", node_type="continue")

    def visit_Return(self, node: ast.Return) -> None:
        """Handle `return` statement."""
        val = ast.unparse(node.value) if node.value else "None"
        self.new_node(f"Return: {val}", shape="box")
        self.last_nodes = []

    def visit_Expr(self, node: ast.Expr) -> None:
        """Handle expression statements."""
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle variable assignment."""
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Handle augmented assignment."""
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Handle annotated assignment."""
        self.new_node(ast.unparse(node).strip(), shape="box")

    def visit_Try(self, node: ast.Try) -> None:
        """
        Handle try...except...finally blocks.

        Try is a risky business.
        1. We attempt the risky code (Try body).
        2. If it blows up, we catch it (Except handlers).
        3. If it works, we might do something else (Else).
        4. No matter what, we clean up (Finally).
        """
        try_node = self.new_node("Try", shape="diamond")

        # 1. Try Body
        self.last_nodes = [(try_node, "Attempt")]
        for stmt in node.body:
            self.visit(stmt)
        
        success_nodes = self.last_nodes
        all_end_nodes = []

        # 2. Exception Handlers
        for handler in node.handlers:
            exc_label = "Exception"
            if handler.type:
                exc_label = f"Exc: {ast.unparse(handler.type)}"
            
            # Conceptually, exceptions branch off the "Try" attempt
            self.last_nodes = [(try_node, exc_label)]
            
            for stmt in handler.body:
                self.visit(stmt)
            
            all_end_nodes.extend(self.last_nodes)

        # 3. Else Block (executed if no exception)
        if node.orelse:
            self.last_nodes = success_nodes
            for stmt in node.orelse:
                self.visit(stmt)
            all_end_nodes.extend(self.last_nodes)
        else:
            all_end_nodes.extend(success_nodes)

        if node.finalbody:
            self.last_nodes = all_end_nodes
            for stmt in node.finalbody:
                self.visit(stmt)
            # Flow continues from end of finally
        else:
            self.last_nodes = all_end_nodes
        
        self.next_edge_label = None

    def visit_Raise(self, node: ast.Raise) -> None:
        """Handle `raise` statement."""
        if node.exc:
            val = ast.unparse(node.exc)
            self.new_node(f"Raise: {val}", shape="box")
        else:
            self.new_node("Raise", shape="box")
        self.last_nodes = []

    def visit_Pass(self, node: ast.Pass) -> None:
        """Handle `pass`."""
        pass

    def generic_visit(self, node: ast.AST) -> None:
        """Fallback for any other node types."""
        if isinstance(node, ast.stmt):
            self.new_node(f"{type(node).__name__}", shape="box")
        else:
            super().generic_visit(node)


def generate_graphviz_flowchart(
    code_str: str,
    title: str = "Flowchart",
    rankdir: str = "TB",
    style_config: Optional[dict[str, str]] = None,
) -> Digraph:
    """
    Parse Python source code and generate a Graphviz Digraph.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        graph = Digraph()
        graph.node(
            "error",
            label="Syntax Error: Cannot parse code",
            shape="box",
            style="filled",
            fillcolor="lightpink",
        )
        return graph

    fc = PythonFlowchartGV(rankdir=rankdir, style_config=style_config)
    fc.visit(tree)
    fc.graph.attr(label=title, labelloc="t", fontsize="20")
    return fc.graph
