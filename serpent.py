"""Launch the Streamlit web application for converting Python functions into flowcharts using Graphviz.

Purpose:
- Clean side-by-side layout: input left, output right.
- Uses modern Streamlit layout features for clarity.
"""

import ast
import shutil

import streamlit as st

from serpent.serpent_graphviz import generate_graphviz_flowchart

# Hide default Streamlit header and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Example placeholder text
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


def main() -> None:
    """Launches the Streamlit web application for converting Python functions into flowcharts using Graphviz.

    Provides a user interface for inputting Python code, specifying a flowchart title,
    and generating a visual flowchart representation. Handles user guidance, error checking,
    and allows downloading the generated flowchart as a PNG image.
    """
    st.set_page_config(
        page_title="SERPENT",
        page_icon="🐍",
        layout="wide"
    )

    st.title("🐍 SERPENT: Python ➜ Flowchart Generator")
    st.caption("Turn your Python functions into clear, standard flowcharts in a few clicks. Fully offline & easy.")

    with st.expander("📌 How to use this tool", expanded=False):
        st.markdown("""
        ✅ Paste valid Python **function(s)** only. \n
        ✅ Indentation must follow Python syntax. \n
        ✅ Comments & docstrings are ignored automatically. \n
        ✅ Add a custom title if you want. \n
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
            placeholder="def my_function(): ..."
        )

        chart_title = st.text_input(
            "🏷️ Flowchart Title",
            value="Python Code Flowchart"
        )

        generate = st.button("✨ Generate Flowchart")

    with output_col:
        st.subheader("🗂️ Output")

        if generate:
            if not code.strip():
                st.warning("⚠️ Please paste some Python code first.")
            else:
                try:
                    # checking if the code is valid Python
                    ast.parse(code)
                    graph = generate_graphviz_flowchart(code, title=chart_title)

                    st.success("✅ Flowchart generated!")
                    st.graphviz_chart(graph.source)

                    if shutil.which("dot"):
                        # Graphviz is available → allow PNG download
                        png_bytes = graph.pipe(format='png')
                        st.download_button(
                            label="📥 Download as PNG",
                            data=png_bytes,
                            file_name="flowchart.png",
                            mime="image/png"
                        )
                    else:
                        # Fallback mode
                        st.warning("⚠️ PNG export not available in this environment.")
                        st.download_button(
                            label="⬇️ Download DOT source",
                            data=graph.source,
                            file_name="flowchart.dot",
                            mime="text/vnd.graphviz"
                        )
                        st.caption("""💡 Tip: Open `.dot` file in VSCode or convert it online to PNG
                                   [e.g. here](https://dreampuf.github.io/GraphvizOnline/).""")

                except Exception as e:
                    st.error(f"❌ Error: Could not parse code.\n\n**Details:** {e}")

    st.markdown("---")
    st.caption("💡 100% offline, no data leaves your machine.")


if __name__ == "__main__":
    main()
