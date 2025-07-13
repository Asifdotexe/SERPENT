# SERPENT

*Syntactic Extraction and Rendering of Python’s End-to-end Node Trees*

![Last Commit](https://img.shields.io/github/last-commit/Asifdotexe/SERPENT)
![Top Language](https://img.shields.io/github/languages/top/Asifdotexe/SERPENT)
![Languages Count](https://img.shields.io/github/languages/count/Asifdotexe/SERPENT)

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [Usage](#usage)
- [Results](#results)
- [Conclusion](#conclusion)
- [License](#license)

---

## Overview

SERPENT is an offline Python flowchart generator. It reads any valid Python code, parses its Abstract Syntax Tree (AST), and converts it into a clear, standard flowchart diagram. This makes it easier to explain, review, and share Python code structure, especially for people who prefer visual formats over raw code. It is designed to work fully offline, without sending any data to online tools or services.

## Getting Started

### Prerequisites
Python 3.8 or above installed on your local machine.

### Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/SERPENT.git
   cd SERPENT
   ```

2. Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Linux/macOS
    venv\Scripts\activate      # On Windows
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

### Usage

* Use the left input panel to paste your valid Python function(s).
* Adjust the flowchart title as needed.
* Click Generate Flowchart to see the visual output side by side.
* Download the flowchart as a PNG for sharing or documentation.

## Results
The project successfully generates Python flowcharts offline. It handles conditional branches, loops, and nested logic, and produces standard flowchart shapes with clean arrows. The tool supports visual clarity, and users can export the diagrams for reports or presentations.

## Conclusion
SERPENT makes reading, explaining, and reviewing Python code easier for developers, students, educators, and teams. By visualising code structure without any online dependencies, it keeps source code secure while improving collaboration and understanding.

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.
