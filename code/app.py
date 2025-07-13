# app.py

"""
Streamlit app for the flowchart tool.
Keeps the frontend fully separate from the logic.
"""
import io
import ast

import streamlit as st
from flowchart_core import PythonFlowchart, draw_flowchart

# Example placeholder text for guidance
placeholder_code = '''\
def example(x):
    if x > 0:
        print("Positive")
    else:
        print("Zero or Negative")
    for i in range(3):
        print(i)
    return x
'''


def main():
    st.title("🧩 Python Code ➜ Flowchart Generator")
    st.subheader("Convert your Python functions into clear flowcharts")

    st.write("""
    This tool reads your Python function and draws a clear flowchart.
    Please follow these simple instructions for best results:
    - Paste only valid Python **function(s)**.
    - The tool **ignores comments and docstrings** in logic.
    - Indentation must be proper Python syntax.
    """)

    # === Let user enter custom chart title ===
    chart_title = st.text_input("Flowchart Title", value="Python Code Flowchart")

    # === Code input area ===
    code = st.text_area("Paste your Python code here:",
                        value=placeholder_code,
                        height=300)

    if st.button("Generate Flowchart"):
        if not code.strip():
            st.warning("Please paste some code first.")
            return

        try:
            # Parse and visit code
            tree = ast.parse(code)
            fc = PythonFlowchart()
            fc.visit(tree)

            # Draw chart, return fig and also save to buffer for download
            fig = draw_flowchart(fc.nodes, fc.edges, title=chart_title)

            st.pyplot(fig)

            # Save figure to a BytesIO buffer for download
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)

            st.download_button(
                label="📥 Download Flowchart as PNG",
                data=buf,
                file_name="flowchart.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"❌ Error parsing code: {e}")


if __name__ == "__main__":
    main()
