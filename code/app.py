# app.py

"""
Streamlit app for the flowchart tool.
Keeps the frontend fully separate from the logic.
"""

import ast

import streamlit as st
from flowchart_core import PythonFlowchart, draw_flowchart


def main():
    st.title("🧩 Python Code ➜ Flowchart Generator")

    code = st.text_area("Paste your Python code here:", height=300)

    if st.button("Generate Flowchart"):
        if not code.strip():
            st.warning("Please paste some code first.")
            return

        try:
            tree = ast.parse(code)
            fc = PythonFlowchart()
            fc.visit(tree)
            fig = draw_flowchart(fc.nodes, fc.edges)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error parsing code: {e}")


if __name__ == "__main__":
    main()
