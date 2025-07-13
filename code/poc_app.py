import ast
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class PythonFlowchart(ast.NodeVisitor):
    """
    Parses Python code using AST to build a visual flowchart structure.
    The main goal is to turn non-visual Python logic into
    an easy-to-follow diagram.
    """

    def __init__(self):
        # This holds all nodes: each is a shape
        # (start/end, process, decision, etc.)
        self.nodes = []
        # Edges connect nodes to define the control flow.
        self.edges = []
        # Ensures every node has a unique ID.
        self.counter = 0
        # Stack tracks the current path through the code for adding edges.
        self.stack = []
        # Used to space nodes vertically so shapes don’t overlap.
        self.y_offset = 0
        # Maps node names to coordinates so arrows know where to start/end.
        self.pos = {}

    def add_node(self, label, shape, x=0):
        """
        Add a node to the flowchart and auto-link it to its parent.
        The X position shifts left/right for branches.
        """
        name = f"n{self.counter}"
        self.counter += 1

        y = -self.y_offset  # Go down as we add nodes.
        self.y_offset += 3

        self.nodes.append((name, label, shape, x, y))
        self.pos[name] = (x, y)

        # By default, connect new node to last node in stack.
        if self.stack:
            self.edges.append((self.stack[-1], name))

        self.stack.append(name)
        return name

    def visit_FunctionDef(self, node):
        """
        Every function starts with a 'start' ellipse and
        ends with an 'end' ellipse.
        This brackets the logic clearly in the diagram.
        """
        self.add_node(f"Function: {node.name}", "start_end")
        self.generic_visit(node)
        self.add_node("End", "start_end")

        # Explicitly connect the last code node to the End.
        self.edges.append((self.stack[-2], self.stack[-1]))
        self.stack.pop()
        self.stack.pop()

    def visit_If(self, node):
        """
        IF statements split the flow left (True) and right (False).
        Both paths then merge back at a join point to restore linear flow.
        """
        cond_node = self.add_node(f"If: {ast.unparse(node.test)}", "decision")

        saved_stack = self.stack.copy()
        base_y = self.y_offset  # Keep both branches aligned vertically.

        # Handle True branch on the left
        self.y_offset = base_y
        self.stack = [cond_node]
        true_nodes = []
        for stmt in node.body:
            true_nodes.append(
                self.add_node(ast.unparse(stmt).strip(), "process", x=-2)
                )
        last_true = true_nodes[-1] if true_nodes else cond_node

        # Handle False branch on the right
        if node.orelse:
            self.y_offset = base_y
            self.stack = [cond_node]
            false_nodes = []
            for stmt in node.orelse:
                false_nodes.append(
                    self.add_node(ast.unparse(stmt).strip(), "process", x=2)
                    )
            last_false = false_nodes[-1]
        else:
            # If there's no else, the decision diamond directly reconnects.
            last_false = cond_node

        # Merge branches at a join circle so the flow continues linearly.
        join_node = self.add_node("Join", "connector", x=0)
        self.edges.append((last_true, join_node))
        if last_false != cond_node:
            self.edges.append((last_false, join_node))
        else:
            self.edges.append((cond_node, join_node))

        self.stack = saved_stack
        self.stack[-1] = join_node

    def visit_For(self, node):
        """
        FOR loops repeat — so we add a loop-back arrow.
        After the loop body, the flow reconnects to the loop header.
        """
        loop_node = self.add_node(
            f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}",
            "loop"
        )
        loop_start = loop_node

        self.generic_visit(node)

        # After loop body, add a connector for loop exit.
        loop_end = self.add_node("Loop End", "connector")

        self.edges.append((self.stack[-2], loop_end))
        # The loop-back edge creates the repeat cycle.
        self.edges.append((loop_end, loop_start))

        self.stack.pop()
        self.stack.pop()

    def visit_While(self, node):
        """
        WHILE loops work the same as FOR loops:
        draw a loop-back arrow so the diagram shows the repeat logic.
        """
        loop_node = self.add_node(f"While: {ast.unparse(node.test)}", "loop")
        loop_start = loop_node

        self.generic_visit(node)

        loop_end = self.add_node("Loop End", "connector")

        self.edges.append((self.stack[-2], loop_end))
        self.edges.append((loop_end, loop_start))

        self.stack.pop()
        self.stack.pop()

    def visit_Return(self, node):
        """
        Return statements mark exit points — so they're normal process boxes.
        """
        self.add_node(f"Return: {ast.unparse(node.value)}", "process")
        self.stack.pop()

    def visit_Expr(self, node):
        """
        Any plain expression (like print) becomes a process box.
        """
        self.add_node(ast.unparse(node).strip(), "process")
        self.stack.pop()


def draw_flowchart(nodes, edges):
    """
    Draws the flowchart with clear shapes and loop-back arrows.
    Uses L-shaped loop-back lines to avoid overlapping nodes.
    """
    fig, ax = plt.subplots(figsize=(8, 14))
    ax.axis("off")

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
            patch = patches.RegularPolygon(
                (x, y), 4, radius=1.5, orientation=0.785,
                facecolor="lightblue", edgecolor="black"
            )
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
            # The loop-back line bends:
            # left, up, right, to avoid crossing shapes.
            side_offset = -3
            mid1 = (x0 + side_offset, y0)
            mid2 = (x0 + side_offset, y1)

            ax.plot(
                [x0, mid1[0]],
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
            # Simple straight line for regular flow.
            ax.annotate(
                "",
                xy=(x1, y1 + dst_offset),
                xytext=(x0, y0 - src_offset),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"),
                annotation_clip=False
            )

    ax.set_xlim(-8, 5)
    ax.set_ylim(min(y for _, _, _, _, y in nodes) - 2, 2)

    plt.title("Python Flowchart — Clean Loops and Joins")
    plt.tight_layout()
    plt.savefig("flowchart_loops_box.png")
    print("✅ Saved: flowchart_loops_box.png")
    plt.show()


if __name__ == "__main__":
    # Small example code to test all shapes and loop-back arrows.
    code = """
def loop_example():
    for i in range(3):
        print(i)
    while True:
        break
    return "Done"
"""
    tree = ast.parse(code)
    flowchart = PythonFlowchart()
    flowchart.visit(tree)
    draw_flowchart(flowchart.nodes, flowchart.edges)
