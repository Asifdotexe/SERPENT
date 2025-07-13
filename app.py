"""
Streamlit app for the Python flowchart tool.

Purpose:
- Clean side-by-side layout: input left, output right.
- Uses modern Streamlit layout features for clarity.
"""

import io
import ast

import streamlit as st
from code.flowchart_core import PythonFlowchart, draw_flowchart

# Hide default Streamlit header and footer
# This is optional, but makes the app look cleaner
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Example placeholder text for clarity
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
    st.set_page_config(page_title="Python ➜ Flowchart Generator",
                       page_icon="🧩",  
                       layout="wide")

    st.title("🧩 Python ➜ Flowchart Generator")
    st.caption("""Turn your Python functions into clear,
               standard flowcharts in a few clicks. fully offline & easy.""")

    with st.expander("📌 How to use this tool", expanded=False):
        st.markdown("""
        ✅ Paste valid Python **function(s)** only.
        ✅ Indentation must follow Python syntax.
        ✅ Comments & docstrings are ignored automatically.
        ✅ Add a custom title if you want.
        ✅ Click **Generate** to see your flowchart side-by-side.
        """)
        st.code(placeholder_code, language="python")

    st.divider()

    # === Side-by-side layout ===
    input_col, output_col = st.columns(2)

    with input_col:
        st.subheader("✏️ Input")
        code = st.text_area(
            "Your Python Code",
            height=350,
            placeholder="def my_function(): ...",
        )

        chart_title = st.text_input("🏷️ Flowchart Title",
                                    value="Python Code Flowchart")

        generate = st.button("✨ Generate Flowchart")

    with output_col:
        st.subheader("🗂️ Output")

        if generate:
            if not code.strip():
                st.warning("⚠️ Please paste some Python code first.")
            else:
                try:
                    tree = ast.parse(code)
                    fc = PythonFlowchart()
                    fc.visit(tree)

                    fig = draw_flowchart(fc.nodes, fc.edges, title=chart_title)

                    st.success("✅ Flowchart generated!")

                    # Download link
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png")
                    buf.seek(0)

                    st.download_button(
                        label="📥 Download PNG",
                        data=buf,
                        file_name="flowchart.png",
                        mime="image/png"
                    )

                    st.pyplot(fig, use_container_width=True)

                except Exception as e:
                    st.error(
                        f"❌ Error: Could not parse code.\n\n**Details:** {e}"
                        )

    st.markdown("---")
    st.caption("💡 100% offline, no data leaves your machine.")


if __name__ == "__main__":
    main()
