"""
Launch the Streamlit web application for converting Python functions into flowcharts.
"""

import ast
import logging
import re
import shutil
import textwrap
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_extras.badges import badge
from streamlit_extras.stylable_container import stylable_container

from serpent.core import generate_graphviz_flowchart
from serpent.resources import EXAMPLES, THEMES

assets_dir = Path(__file__).parent / "assets"
try:
    LOGO = Image.open(assets_dir / "serpent_logo_transparent.png")
    ICON = (
        Image.open(assets_dir / "serpent_logo_compact.png")
        if (assets_dir / "serpent_logo_compact.png").exists()
        else LOGO
    )
except (FileNotFoundError, OSError):
    LOGO = None
    ICON = None

# Page Configuration
st.set_page_config(
    page_title="SERPENT",
    page_icon=ICON or "🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for cleaner look
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button {width: 100%;}
    /* Hide top padding */
    .block-container {padding-top: 2rem;}
    </style>
""",
    unsafe_allow_html=True,
)


def main() -> None:
    """Main application entry point."""

    with st.sidebar:
        if LOGO:
            st.image(LOGO, width="stretch")
        else:
            st.title("SERPENT 🐍")

        st.write("Turn your Python functions into clear flowcharts.")
        st.divider()

        def update_example():
            """Callback to update code input when example changes."""
            ex = st.session_state.example_selector
            if ex != "(Custom)":
                st.session_state.code_area_widget = EXAMPLES[ex]
                st.session_state.code_input = EXAMPLES[ex]

        st.subheader("⚙️ Settings")

        selected_example = st.selectbox(
            "Load Example",
            ["(Custom)"] + list(EXAMPLES.keys()),
            index=0,
            help="Select an example to see how it works.",
            key="example_selector",
            on_change=update_example,
        )

        st.caption("Appearance")
        rankdir = st.selectbox(
            "Orientation",
            options=["TB", "LR"],
            format_func=lambda x: "Top-Down" if x == "TB" else "Left-Right",
        )

        theme_name = st.selectbox("Theme", options=list(THEMES.keys()))

        st.divider()

        with st.expander("About & Help"):
            st.markdown(
                """
            **How to use:**
            1. Paste your Python function.
            2. The flowchart updates automatically.
            3. Download the result.

            **Tips:**
            - Works best with single functions.
            - Supports `if/else`, `loops`, `break/continue`.
            """
            )

            st.caption("Created by Asif Sayyed")
            badge(
                type="github",
                name="Asifdotexe/SERPENT",
                url="https://github.com/Asifdotexe/SERPENT",
            )

    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.title("Flowchart Generator")

    input_col, output_col = st.columns(2)

    with input_col:
        st.subheader("📝 Input Code")

        if selected_example != "(Custom)":
            default_code = EXAMPLES[selected_example]
        else:
            # Keep previous input if possible, else empty
            default_code = "def my_func():\n    pass"

        # Initial state
        if "code_input" not in st.session_state:
            st.session_state.code_input = default_code

        # We handle updates via callback now, so we remove the imperative check
        code = st.text_area(
            "Python Code",
            value=st.session_state.code_input,
            height=400,
            label_visibility="collapsed",
            key="code_area_widget",
        )

        # Sync widget back to session state for manual edits
        if code != st.session_state.code_input:
            st.session_state.code_input = code
            if selected_example != "(Custom)":
                # If user edits an example, switch dropdownto Custom
                # (This requires rerun, effectively)
                pass

        chart_title = st.text_input(
            "Chart Title", placeholder="Enter a title (optional)"
        )

    with output_col:
        st.subheader("🖼️ Flowchart")

        with stylable_container(
            key="output_container",
            css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: 1rem;
                min-height: 480px;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: rgba(255, 255, 255, 0.05);
            }
            """,
        ):
            valid_graph = None
            if not code.strip():
                st.info("Waiting for code input...")
            else:
                try:
                    # Validate
                    ast.parse(code)

                    # Generate
                    final_title = chart_title or "Flowchart"
                    selected_theme = THEMES[theme_name]

                    graph = generate_graphviz_flowchart(
                        code,
                        title=final_title,
                        rankdir=rankdir,
                        style_config=selected_theme,
                    )

                    st.graphviz_chart(graph, width="stretch")

                    # Store for download buttons below
                    valid_graph = graph

                except SyntaxError as e:
                    st.error(f"Syntax Error: {e}")
                    valid_graph = None
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    logging.exception("Graph generation failed")
                    valid_graph = None

    # Download Area (Full width below columns)
    if "valid_graph" in locals() and valid_graph:
        st.divider()
        d_col1, d_col2 = st.columns([1, 1])

        # Sanitize filename
        safe_title = re.sub(
            r"[^a-z0-9_\-]", "", (chart_title or "flowchart").lower().replace(" ", "_")
        )

        with d_col1:
            if shutil.which("dot"):
                try:
                    png_bytes = valid_graph.pipe(format="png")
                    st.download_button(
                        "📥 Download PNG",
                        data=png_bytes,
                        file_name=f"{safe_title}.png",
                        mime="image/png",
                        width="stretch",
                    )
                except Exception:
                    st.warning("Could not generate PNG (Check Graphviz installation).")

        with d_col2:
            st.download_button(
                "📄 Download DOT",
                data=valid_graph.source,
                file_name=f"{safe_title}.dot",
                mime="text/vnd.graphviz",
                width="stretch",
            )


if __name__ == "__main__":
    main()
