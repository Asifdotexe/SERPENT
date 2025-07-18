"""
Core logic for parsing Python code with AST and drawing a flowchart.
This module stays independent of any UI or web code.
"""

import ast
from graphviz import Digraph


class PythonFlowchartGV(ast.NodeVisitor):
    def __init__(self):
        self.graph = Digraph(format='png')
        self.counter = 0
        self.stack = []

    def new_node(self, label, shape="box"):
        name = f"n{self.counter}"
        self.counter += 1
        self.graph.node(name, label=label, shape=shape)
        if self.stack:
            self.graph.edge(self.stack[-1], name)
        self.stack.append(name)
        return name

    def visit_FunctionDef(self, node):
        self.new_node(f"Function: {node.name}", "oval")
        self.generic_visit(node)
        self.stack.pop()

    def visit_If(self, node):
        cond = self.new_node(f"If: {ast.unparse(node.test)}", "diamond")
        parent = self.stack[-1]  # Save current point before branching

        # === True branch ===
        self.stack = [cond]
        for stmt in node.body:
            self.visit(stmt)
        true_end = self.stack[-1]

        # === False branch ===
        if node.orelse:
            self.stack = [cond]
            for stmt in node.orelse:
                self.visit(stmt)
            false_end = self.stack[-1]

            # Reconnect last false and true ends to next node (if needed)
            self.stack = [false_end]  # Keep false branch as latest point
        else:
            self.stack = [true_end]  # Continue from true branch if no else

    def visit_For(self, node):
        self.new_node(f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}", "circle")
        self.generic_visit(node)
        self.stack.pop()

    def visit_While(self, node):
        self.new_node(f"While: {ast.unparse(node.test)}", "circle")
        self.generic_visit(node)
        self.stack.pop()

    def visit_Expr(self, node):
        if isinstance(node.value, (ast.Str, ast.Constant)):
            return
        self.new_node(ast.unparse(node).strip(), "box")
        self.stack.pop()

    def visit_Return(self, node):
        self.new_node(f"Return: {ast.unparse(node.value)}", "box")
        self.stack.pop()


def generate_graphviz_flowchart(code_str: str, title="Flowchart"):
    tree = ast.parse(code_str)
    fc = PythonFlowchartGV()
    fc.visit(tree)
    fc.graph.attr(label=title, labelloc="t", fontsize="20")
    return fc.graph
