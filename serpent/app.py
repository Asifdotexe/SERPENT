"""
Launch the Streamlit web application for converting Python functions into flowcharts using Graphviz.

Purpose:
- Clean side-by-side layout with custom styling.
- Uses modern Streamlit layout features for clarity.
"""

import ast
import shutil
import textwrap
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_extras.avatar import avatar
from streamlit_extras.badges import badge
from streamlit_extras.stylable_container import stylable_container

from serpent.core import generate_graphviz_flowchart

assets_dir = Path(__file__).parent.parent / "assets"
try:
    logo = Image.open(assets_dir / "serpent_logo_transparent.png")
    banner = Image.open(assets_dir / "serpent_banner_transparent.png")
except FileNotFoundError:
    # Fallback to no images if not found (safer for package distribution if assets aren't included yet)
    logo = None
    banner = None

# Page Configuration
st.set_page_config(
    page_title="SERPENT",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Just hiding the boring default Streamlit menu and footer.
# Also making buttons full width because big buttons are clickable buttons.
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button {width: 100%;}
    </style>
""",
    unsafe_allow_html=True,
)

# A little sample to show user what to do.
placeholder_code = textwrap.dedent("""\
    def should_i_code_today(coffee_level: int, deadline_approaching: bool) -> str:
        if deadline_approaching:
            return "Code like your life depends on it!"
        elif coffee_level > 5:
            return "Let's write some beautiful, elegant code."
        else:
            return "Go get more coffee, then we'll talk."
""")


def main() -> None:
    """
    Launch the Streamlit web application.

    This is the main entry point. It paints the UI, takes the user input,
    calls the generator, and serves the hot, fresh flowchart.
    """
    if banner:
        st.image(banner, use_container_width=True)
    else:
        # Fallback title
        st.title("SERPENT")

    st.caption(
        "Turn your Python functions into clear, standard flowcharts in a few clicks."
    )

    # Using avatar to show who's the boss (author).
    avatar(
        [
            {
                "url": "https://avatars.githubusercontent.com/u/115421661?v=4",
                "size": 40,
                "title": "Asif Sayyed",
                "caption": "Hey, turn your code into a flowchart and turn knowledge sharing into a breeze.",
                "key": "author_avatar",
            }
        ]
    )

    with st.expander("How to use this tool?"):
        st.markdown("""
        1.  **Paste your code**: Drop a valid Python function into the text area.
        2.  **Add a title**: Give your flowchart a descriptive title.
        3.  **Generate**: Click the button to see your flowchart appear side-by-side.
        """)
        st.code(placeholder_code, language="python")

    st.divider()

    # Side-by-side layout (make 2 columns)
    input_col, output_col = st.columns(2)

    # Input Column
    with (
        input_col,
        stylable_container(
            key="input_container",
            css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
            }
        """,
        ),
    ):
        st.subheader("Input")
        code = st.text_area(
            "Your Python Code",
            height=350,
            placeholder="def my_function(): ...",
            help="Paste a valid Python function here, The script will ignore comments and docstrings.",
        )
        chart_title = st.text_input(
            "Flowchart Title",
            value="Some fancy title for your flowchart?",
            help="Enter a title to be displayed at the top of your flowchart.",
        )
        generate = st.button(
            "Generate Flowchart",
            help="Click here to generate the flowchart from your code.",
            type="primary",
            use_container_width=True,
        )

    # Output Column
    with (
        output_col,
        stylable_container(
            key="output_container",
            css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
            }
        """,
        ),
    ):
        st.subheader("Output")

        if not generate:
            st.info("Your generated flowchart will appear here.")
        elif not code.strip():
            st.warning(
                "Please paste some Python code first. Can't make juice without oranges!"
            )
        else:
            try:
                # Validating input first. Safety first!
                ast.parse(code)
                graph = generate_graphviz_flowchart(code, title=chart_title)
                st.success("✅ Flowchart generated! Looking good.")
                st.graphviz_chart(graph.source)

                # Download Buttons
                # If 'dot' is installed, we can give a PNG. If not, only DOT file.
                # TODO: Implement PNG download functionality
                if shutil.which("dot"):
                    png_bytes = graph.pipe(format="png")
                    st.download_button(
                        label="📥 Download as PNG",
                        data=png_bytes,
                        file_name=f"{chart_title.replace(' ', '_').lower()}.png",
                        mime="image/png",
                        help="Download the flowchart as a PNG image.",
                        use_container_width=True,
                        type="primary",
                    )
                else:
                    st.warning(
                        "PNG export not available. Install `Graphviz` system-wide to enable it."
                    )
                    st.download_button(
                        label="⬇️ Download DOT source",
                        data=graph.source,
                        file_name=f"{chart_title.replace(' ', '_').lower()}.dot",
                        mime="text/vnd.graphviz",
                        help="Download the Graphviz source file (.dot) to render it locally.",
                    )
                    st.caption("💡 Tip: You can view `.dot` files in VSCode or online.")

            except SyntaxError as e:
                st.error(
                    f"Syntax Error: Your Python code is invalid.\n\n**Details:** {e}"
                )
            except Exception as e:
                st.error(
                    f"An unexpected error occurred. Something broke!\n\n**Details:** {e}"
                )

    st.divider()
    st.caption("Like the result? Starring the repository helps a lot!")
    badge(
        type="github",
        name="Asifdotexe/SERPENT",
        url="https://github.com/Asifdotexe/SERPENT",
    )


if __name__ == "__main__":
    main()
