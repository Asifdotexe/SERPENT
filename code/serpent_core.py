# serpent_core.py

"""
Core logic for parsing Python code with AST and drawing a flowchart.
This module stays independent of any UI or web code.
"""

import ast

import matplotlib.patches as patches
import matplotlib.pyplot as plt


class PythonFlowchart(ast.NodeVisitor):
    """
    Core logic for AST ➜ Flowchart.
    Now ignores docstrings so they do not appear as code steps.
    """


    def __init__(self):
        """
        Initialize the PythonFlowchart with empty node and edge lists, a unique node counter, a stack for traversal, a vertical offset for layout, and a position dictionary for node coordinates.
        """
        self.nodes = []
        self.edges = []
        self.counter = 0
        self.stack = []
        self.y_offset = 0
        self.pos = {}


    def _strip_docstring(self, body):
        """
        Remove a leading docstring expression from a list of AST nodes if present.
        
        Parameters:
            body (list): List of AST nodes representing a code block.
        
        Returns:
            list: The input list with the first node removed if it is a docstring expression; otherwise, the original list.
        """
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, (ast.Str, ast.Constant))
        ):
            return body[1:]
        return body


    def add_node(self, label, shape, x=0, y=None):
        """
        Add a new flowchart node with the specified label and shape, automatically assigning a unique name and layout position.
        
        Parameters:
        	label (str): The text label for the node.
        	shape (str): The type of flowchart shape (e.g., 'process', 'decision').
        	x (int, optional): The x-coordinate for the node. Defaults to 0.
        	y (int, optional): The y-coordinate for the node. If not provided, an automatic vertical offset is used.
        
        Returns:
        	name (str): The unique identifier assigned to the newly added node.
        """
        name = f"n{self.counter}"
        self.counter += 1
        if y is None:
            y = -self.y_offset
            self.y_offset += 3

        self.nodes.append((name, label, shape, x, y))
        self.pos[name] = (x, y)

        if self.stack:
            self.edges.append((self.stack[-1], name))

        self.stack.append(name)
        return name


    def visit_FunctionDef(self, node):
        """
        Processes a function definition node, adding a start/end node for the function and visiting its body after removing any leading docstring.
        """
        self.add_node(f"Function: {node.name}", "start_end")
        node.body = self._strip_docstring(node.body)
        self.generic_visit(node)
        self.stack.pop()


    def visit_ClassDef(self, node):
        """
        Processes a class definition node by adding a start/end node for the class, stripping any leading docstring, visiting its body, and updating the node stack.
        """
        self.add_node(f"Class: {node.name}", "start_end")
        node.body = self._strip_docstring(node.body)
        self.generic_visit(node)
        self.stack.pop()


    def visit_If(self, node):
        """
        Processes an `if` statement node, creating a decision node, separate branches for true and false bodies, and a join connector node to merge control flow.
        
        This method ensures correct flowchart structure for nested and sequential statements within both branches, maintaining layout consistency and accurate edge connections.
        """
        cond_node = self.add_node(f"If: {ast.unparse(node.test)}", "decision")
        saved_stack = self.stack.copy()
        y_base = self.y_offset

        # True branch
        self.y_offset = y_base
        self.stack = [cond_node]
        true_last_node = cond_node
        if node.body:
            for stmt in node.body:
                self.visit(stmt)
            true_last_node = self.stack[-1]

        # False branch (if exists)
        self.y_offset = y_base
        self.stack = [cond_node]
        false_last_node = cond_node
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)
            false_last_node = self.stack[-1]

        # Join node
        join_y = -max(self.y_offset, y_base)
        join_node = f"n{self.counter}"
        self.counter += 1
        self.nodes.append((join_node, "Join", "connector", 0, join_y))
        self.pos[join_node] = (0, join_y)

        if true_last_node != cond_node:
            self.edges.append((true_last_node, join_node))
        else:
            self.edges.append((cond_node, join_node))

        if false_last_node != cond_node:
            self.edges.append((false_last_node, join_node))
        else:
            self.edges.append((cond_node, join_node))

        self.stack = saved_stack
        self.stack[-1] = join_node
        self.y_offset += 3


    def visit_For(self, node):
        """
        Visit a for-loop AST node and add a corresponding loop node to the flowchart.
        
        Adds a loop node labeled with the loop target and iterable, traverses the loop body, and updates the flowchart structure accordingly.
        """
        self.add_node(
            f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}",
            "loop"
        )
        self.generic_visit(node)
        self.stack.pop()

    def visit_While(self, node):
        """Standard While loop with backward link."""
        self.add_node(f"While: {ast.unparse(node.test)}", "loop")
        self.generic_visit(node)
        self.stack.pop()

    def visit_Return(self, node):
        """Return is a process step."""
        self.add_node(f"Return: {ast.unparse(node.value)}", "process")
        self.stack.pop()

    def visit_Expr(self, node):
        """Skip non-docstring expressions, treat as process."""
        if isinstance(node.value, (ast.Str, ast.Constant)):
            return  # Skip docstrings if any slipped through
        self.add_node(ast.unparse(node).strip(), "process")
        self.stack.pop()


def draw_flowchart(nodes, edges, title="Flowchart"):
    """Plots the flowchart from nodes + edges with Matplotlib."""
    fig, ax = plt.subplots(figsize=(8, 12))
    ax.axis("off")
    ax.set_aspect('equal')

    pos = {name: (x, y) for name, _, _, x, y in nodes}

    for name, label, shape, x, y in nodes:
        if shape == "start_end":
            patch = patches.Ellipse((x, y), 3, 1.5,
                                    facecolor="lightgreen",
                                    edgecolor="black")
        elif shape == "process":
            patch = patches.Rectangle((x - 1.5, y - 0.75), 3, 1.5,
                                      facecolor="orange",
                                      edgecolor="black")
        elif shape == "decision":
            patch = patches.RegularPolygon((x, y), 4, radius=1.5,
                                           orientation=0.785,
                                           facecolor="lightblue",
                                           edgecolor="black")
        elif shape == "loop":
            patch = patches.Circle((x, y), radius=1.2,
                                   facecolor="pink",
                                   edgecolor="black")
        elif shape == "connector":
            patch = patches.Circle((x, y), radius=0.4,
                                   facecolor="grey",
                                   edgecolor="black")
        else:
            continue

        ax.add_patch(patch)
        ax.text(x, y, label, ha="center", va="center", fontsize=8, wrap=True)

    def shape_offset(shape):
        return {
            "start_end": 0.8,
            "process": 0.8,
            "decision": 1.2,
            "loop": 1.2,
            "connector": 0.4
        }.get(shape, 0.8)

    for src, dst in edges:
        x0, y0 = pos[src]
        x1, y1 = pos[dst]

        src_shape = [n for n in nodes if n[0] == src][0][2]
        dst_shape = [n for n in nodes if n[0] == dst][0][2]
        src_offset = shape_offset(src_shape)
        dst_offset = shape_offset(dst_shape)

        if y1 > y0:
            side_offset = -3
            mid1 = (x0 + side_offset, y0)
            mid2 = (x0 + side_offset, y1)

            ax.plot([x0, mid1[0]],
                    [y0 + src_offset, mid1[1] + src_offset],
                    'k-', lw=1.2)

            ax.plot([mid1[0], mid2[0]],
                    [mid1[1] + src_offset, mid2[1] - dst_offset],
                    'k-', lw=1.2)

            ax.plot([mid2[0], x1],
                    [mid2[1] - dst_offset, y1 - dst_offset],
                    'k-', lw=1.2)

            ax.annotate(
                "",
                xy=(x1, y1 - dst_offset),
                xytext=(mid2[0], mid2[1] - dst_offset),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"),
                annotation_clip=False
            )
        else:
            ax.annotate(
                "",
                xy=(x1, y1 + dst_offset),
                xytext=(x0, y0 - src_offset),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"),
                annotation_clip=False
            )

    ax.set_xlim(-8, 5)
    ax.set_ylim(min(y for _, _, _, _, y in nodes) - 2, 2)

    plt.title(title)
    plt.tight_layout()
    return fig
