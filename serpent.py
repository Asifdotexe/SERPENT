"""Launch the Streamlit web application for converting Python functions into flowcharts using Graphviz.

Purpose:
- Clean side-by-side layout: input left, output right.
- Uses modern Streamlit layout features for clarity.
"""

import ast
import shutil
import textwrap
from PIL import Image

import streamlit as st

from serpent_scripts.serpent_graphviz import generate_graphviz_flowchart

# --- Load assets ---
logo = Image.open(r'..\SERPENT\examples\serpent_logo_transparent.png')
banner = Image.open(r'..\SERPENT\examples\serpent_banner_transparent.png')

# --- Page Configuration ---
st.set_page_config(
    page_title="SERPENT",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="collapsed"
    )

# -- Custom CSS to hide default Streamlit header and footer --
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       .stButton>button {width: 100%;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# --- Placeholder and example code ---
placeholder_code = textwrap.dedent("""\
    def should_i_code_today(coffee_level, deadline_approaching):
        if deadline_approaching:
            return "Code like your life depends on it!"
        elif coffee_level > 5:
            return "Let's write some beautiful, elegant code."
        else:
            return "Go get more coffee, then we'll talk."
""")


# --- Main application logic ---
def main() -> None:
    """Launches the Streamlit web application for converting Python functions into flowcharts using Graphviz.
    """
    st.image(banner, use_container_width=True)
    st.caption("Turn your Python functions into clear, standard flowcharts in a few clicks. Fully locally & easy.")

    with st.expander("📌 How to use this tool", expanded=False):
        st.markdown("""
        1.  **Paste your code**: Drop a valid Python function into the text area.
        2.  **Add a title**: Give your flowchart a descriptive title.
        3.  **Generate**: Click the button to see your flowchart appear side-by-side.
        """)
        st.code(placeholder_code, language="python")

    st.divider()

    # --- Side-by-side layout ---
    input_col, output_col = st.columns(2)

    with input_col:
        st.subheader("Input")
        code = st.text_area(
            "Your Python Code",
            height=350,
            placeholder="def my_function(): ...",
            help="Paste one or more valid Python functions here. The script will ignore comments and docstrings."
        )

        chart_title = st.text_input(
            "🏷️ Flowchart Title",
            value="Python Code Flowchart",
            help="Enter a title to be displayed at the top of your flowchart."
        )

        generate = st.button(
            "Generate Flowchart",
            help="Click here to generate the flowchart from your code.",
            type="primary",
            use_container_width=True,
            icon=":material/flowchart:"
        )

    with output_col:
        st.subheader("Output")

        if not generate:
            st.info("Your generated flowchart will appear here.")
            return

        if not code.strip():
            st.warning("⚠️ Please paste some Python code first.")
            return

        try:
            # --- Code Validation and Flowchart Generation ---
            ast.parse(code)
            graph = generate_graphviz_flowchart(code, title=chart_title)

            st.success("✅ Flowchart generated!")
            st.graphviz_chart(graph.source)

            # --- Download Buttons ---
            if shutil.which("dot"):
                # Graphviz is available → allow PNG download
                png_bytes = graph.pipe(format='png')
                st.download_button(
                    label="📥 Download as PNG",
                    data=png_bytes,
                    file_name=f"{chart_title.replace(' ', '_').lower()}.png",
                    mime="image/png",
                    help="Download the flowchart as a PNG image.",
                    use_container_width=True,
                    type='primary'
                )
            else:
                # Fallback mode
                st.warning("⚠️ PNG export not available in this environment.")
                st.download_button(
                    label="⬇️ Download DOT source",
                    data=graph.source,
                    file_name=f"{chart_title.replace(' ', '_').lower()}.dot",
                    mime="text/vnd.graphviz",
                    help="Download the Graphviz source file (.dot) to render it locally."
                )
                st.caption("""💡 Tip: Open `.dot` file in VSCode or convert it online to PNG
                            [e.g. here](https://dreampuf.github.io/GraphvizOnline/).""")

        except SyntaxError as e:
            st.error(f"❌ Syntax Error: Your Python code is invalid.\n\n**Details:** {e}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred.\n\n**Details:** {e}")

    st.markdown("---")
    st.caption("💡 100% offline, no data leaves your machine.")


if __name__ == "__main__":
    main()
