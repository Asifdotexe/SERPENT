"""
This streamlit application is a proof of concept code to test out tech stack
"""

import streamlit as st
from pyflowchart import Flowchart

st.set_page_config(page_title="Code to Flowchart", layout="wide")
st.title("🗂️ Code to Flowchart Visualizer")


code_input = st.text_area(
    "Paste your Python code here:",
    height=300,
    placeholder="""def greet(name):\n    if name:\n        
    print(f'Hello, {name}')\n    else:\n        print('Hello, World!')""",
)

if st.button("Generate Flowchart"):
    if not code_input.strip():
        st.warning("Please paste some Python code first!")
    else:
        try:
            fc = Flowchart.from_code(code_input)
            flowchart_js_code = fc.flowchart()

            flowchart_html = f"""
            <div id="canvas"></div>

            <!-- Load flowchart.js -->
            <script src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.15.0/flowchart.min.js"></script>

            <script>
            document.addEventListener("DOMContentLoaded", function() {{
                var diagram = flowchart.parse(`{flowchart_js_code}`);
                diagram.drawSVG('canvas');
            }});
            </script>
            """

            st.components.v1.html(flowchart_html, height=500, scrolling=True)

        except Exception as e:
            st.error(f"Error generating flowchart: {e}")
