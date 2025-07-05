"""
This script takes the path to the code file and then convert them into flowcharts
and save at the desired location
"""

import argparse
from pyflowchart import Flowchart

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Flowchart</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.15.0/flowchart.min.js"></script>
</head>
<body>
  <div id="canvas"></div>
  <script>
    var diagram = flowchart.parse(`{}`);
    diagram.drawSVG('canvas');
  </script>
</body>
</html>
"""

def main():
    """
    Runner function
    """
    parser = argparse.ArgumentParser(description="Convert Python code to flowchart syntax & HTML")
    parser.add_argument("input",
                        help="Path to the input Python file")
    parser.add_argument("-o", "--output",
                        help="Path to save HTML output", default="flowchart.html")

    args = parser.parse_args()

    with open(args.input, "r") as f:
        code = f.read()

    fc = Flowchart.from_code(code)
    flowchart_js_code = fc.flowchart()

    html_output = HTML_TEMPLATE.format(flowchart_js_code)

    with open(args.output, "w") as f:
        f.write(html_output)

    print(f"Flowchart HTML saved to: {args.output}")

if __name__ == "__main__":
    main()
