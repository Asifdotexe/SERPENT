# Code2Flow

This tool provides a simple and efficient way to transform Python code into clear, interactive flowcharts. It's designed to help developers, educators, and interviewees visualize and present the logical structure of their code with ease.

---

## Features

* **Code Parsing:** Converts Python scripts or functions into flowchart syntax using `pyflowchart`.
* **Visual Rendering:** Generates interactive diagrams from the flowchart syntax using `flowchart.js`.
* **Export Options:** Allows users to download flowcharts in various formats, including PNG, PDF, and standalone HTML.
* **User-Friendly Interface:** Provides a straightforward and responsive web interface built with Streamlit or Gradio for code input, preview, and download.
* **Reusable Core:** The backend logic for parsing and rendering is designed to be modular, enabling its use in other applications or development pipelines.
* **Basic Syntax Highlighting:** Improves readability of the input code.
* **Customizable Styling:** Offers options to adjust the flowchart's visual style, such as color themes.

---

## Scope

### In Scope

* **Input:** Accepts Python code via a `.py` file upload or direct text input.
* **Output:** Generates a visual flowchart that can be exported as PNG, PDF, or HTML.
* **Framework:** Developed as a single-user local web application (Streamlit or Gradio).
* **Code Presentation:** Includes basic syntax highlighting for input code.
* **Styling:** Provides options for minor style adjustments (e.g., color themes).

### Out of Scope (for now)

* **Multi-language Support:** Does not support languages beyond Python (e.g., C++, Java).
* **Complex Python Constructs:** Advanced Python features like metaprogramming or decorators are not guaranteed to be fully represented unless handled by `pyflowchart`.
* **Advanced Collaborative Editing:** Does not support real-time collaboration.
* **Scalable Hosting:** Not designed for large-scale deployment or hosting.

---

## Use Cases

### For Students & Educators

* **Learning Aid:** Visualize the step-by-step execution of code.
* **Teaching Tool:** Effectively explain algorithms and control flow concepts.

### For Developers & Teams

* **Code Audit:** Quickly understand the structure of unfamiliar scripts.
* **Documentation:** Create visual documentation for existing or legacy codebases.

### For Job Interviews & Demos

* **Candidate Demonstration:** Candidates can visually articulate their coding thought process.
* **Recruiter Assessment:** Recruiters can gain better insights into a candidate's code comprehension.

### For Technical Documentation

* **Embedded Diagrams:** Integrate flowcharts into wikis, READMEs, or client deliverables for enhanced clarity.