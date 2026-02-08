"""
Launch the Streamlit web application for converting Python functions into flowcharts.
"""

import ast
import re
import shutil
import logging
import textwrap
from pathlib import Path
from typing import Dict, Any

import streamlit as st
from PIL import Image
from streamlit_extras.badges import badge
from streamlit_extras.stylable_container import stylable_container

from serpent.core import generate_graphviz_flowchart

assets_dir = Path(__file__).parent / "assets"
try:
    logo = Image.open(assets_dir / "serpent_logo_transparent.png")
    icon = Image.open(assets_dir / "serpent_logo_compact.png") if (assets_dir / "serpent_logo_compact.png").exists() else logo
except FileNotFoundError:
    logo = None
    icon = None

# Page Configuration
st.set_page_config(
    page_title="SERPENT",
    page_icon=icon or "🐍",
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

# --- Themes ---
THEMES: Dict[str, Dict[str, str]] = {
    "Classic (Pastel)": {
        "box": "lightyellow",
        "diamond": "lightblue",
        "oval": "lightgreen",
        "circle": "thistle",
        "parallelogram": "lightcyan",
        "break": "mistyrose",
        "continue": "lightgray",
    },
    "Clean White": {
        "box": "white",
        "diamond": "white",
        "oval": "white",
        "circle": "white",
        "parallelogram": "white",
        "break": "white",
        "continue": "white",
    },
    "Dark Mode": {
        "box": "#444444",
        "diamond": "#555555",
        "oval": "#222222",
        "circle": "#666666",
        "parallelogram": "#333333",
        "break": "#883333",
        "continue": "#333388",
        # Note: Text color handling would require more core changes, 
        # so this is a "dark cards" theme for now.
    },
    "Blueberry": {
        "box": "#e3f2fd",
        "diamond": "#bbdefb",
        "oval": "#90caf9",
        "circle": "#64b5f6",
        "parallelogram": "#42a5f5",
        "break": "#ffcdd2",
        "continue": "#e1bee7",
    }
}

# --- Examples ---
EXAMPLES = {
    "Motivation Check": textwrap.dedent("""\
        def should_i_code_today(coffee_level: int, deadline_approaching: bool) -> str:
            if deadline_approaching:
                return "Code like your life depends on it!"
            elif coffee_level > 5:
                # Caffeine power!
                return "Let's write some beautiful, elegant code."
            else:
                return "Go get more coffee, then we'll talk."
    """),
    "Bug Fix Loop": textwrap.dedent("""\
        def fix_bugs(bugs: int):
            while bugs > 0:
                print("Fixing a bug...")
                bugs -= 1
                if bugs % 5 == 0:
                    print("Created a new bug by accident!")
                    bugs += 1
            print("Production ready!")
    """),
    "Data Processing": textwrap.dedent("""\
        def process_data(data: list[int]) -> list[int]:
            result = []
            for item in data:
                if item < 0:
                    continue  # Skip negative numbers
                
                if item > 100:
                    break     # Stop if too large
                
                result.append(item * 2)
            return result
    """),
}


def main() -> None:
    """Main application entry point."""
    
    # --- Sidebar ---
    with st.sidebar:
        if logo:
            st.image(logo, use_container_width=True)
        else:
            st.title("SERPENT 🐍")
        
        st.write("Turn your Python functions into clear flowcharts.")
        st.divider()
        
        st.subheader("⚙️ Settings")
        
        # 1. Example Loader
        selected_example = st.selectbox(
            "Load Example",
            ["(Custom)"] + list(EXAMPLES.keys()),
            index=0,
            help="Select an example to see how it works."
        )
        
        # 2. Appearance
        st.caption("Appearance")
        col1, col2 = st.columns(2)
        with col1:
            rankdir = st.selectbox(
                "Orientation", 
                options=["TB", "LR"], 
                format_func=lambda x: "Top-Down" if x == "TB" else "Left-Right"
            )
        with col2:
            theme_name = st.selectbox("Theme", options=list(THEMES.keys()))
        
        st.divider()
        
        with st.expander("About & Help"):
            st.markdown("""
            **How to use:**
            1. Paste your Python function.
            2. Click **Generate**.
            3. Download the result.
            
            **Tips:**
            - Works best with single functions.
            - Supports `if/else`, `loops`, `break/continue`.
            """)
            
            st.caption("Created by Asif Sayyed")
            badge(
                type="github",
                name="Asifdotexe/SERPENT",
                url="https://github.com/Asifdotexe/SERPENT",
            )

    # --- Main Content ---
    
    # Header handling
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.title("Flowchart Generator")
    
    # Layout
    input_col, output_col = st.columns(2)

    # --- Input Section ---
    with input_col:
        st.subheader("📝 Input Code")
        
        # Determine code to show
        if selected_example != "(Custom)":
            default_code = EXAMPLES[selected_example]
        else:
            # Keep previous input if possible, else empty
            default_code = "def my_func():\n    pass"

        # Use session state to handle example updates
        if "code_input" not in st.session_state:
            st.session_state.code_input = default_code
        
        # Update session state if example changed
        if selected_example != "(Custom)" and st.session_state.get("last_example") != selected_example:
            st.session_state.code_input = default_code
            st.session_state.last_example = selected_example
        
        code = st.text_area(
            "Python Code",
            value=st.session_state.code_input,
            height=400,
            label_visibility="collapsed",
            key="code_area_widget"
        )
        
        # Sync widget back to session state for manual edits
        if code != st.session_state.code_input:
            st.session_state.code_input = code
            if selected_example != "(Custom)":
                # If user edits an example, switch dropdownto Custom
                # (This requires rerun, effectively)
                pass 

        chart_title = st.text_input("Chart Title", placeholder="Enter a title (optional)")
        
        generate_btn = st.button("Generate Flowchart", type="primary", use_container_width=True)

    # --- Output Section ---
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
                justify_content: center;
                background-color: rgba(255, 255, 255, 0.05);
            }
            """,
        ):
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
                        style_config=selected_theme
                    )
                    
                    st.graphviz_chart(graph, use_container_width=True)
                    
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
    if 'valid_graph' in locals() and valid_graph:
        st.divider()
        d_col1, d_col2 = st.columns([1, 1])
        
        # Sanitize filename
        safe_title = re.sub(r"[^a-z0-9_\-]", "", (chart_title or "flowchart").lower().replace(" ", "_"))
        
        with d_col1:
             if shutil.which("dot"):
                try:
                    png_bytes = valid_graph.pipe(format="png")
                    st.download_button(
                        "📥 Download PNG",
                        data=png_bytes,
                        file_name=f"{safe_title}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                except Exception:
                    st.warning("Could not generate PNG (Check Graphviz installation).")
        
        with d_col2:
            st.download_button(
                "📄 Download DOT",
                data=valid_graph.source,
                file_name=f"{safe_title}.dot",
                mime="text/vnd.graphviz",
                use_container_width=True
            )


if __name__ == "__main__":
    main()
