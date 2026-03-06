"""Export tools for saving research reports in various formats.

Provides tools for exporting markdown content to markdown files and
professionally formatted PDF documents.
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from datetime import datetime


class ExportInput(BaseModel):
    """Input schema for export tools."""

    content: str = Field(..., description="Content to export")
    filename: str = Field(..., description="Output filename (without extension)")


class MarkdownExportTool(BaseTool):
    """Tool for exporting content to markdown files."""

    name: str = "export_markdown"
    description: str = "Export content to a markdown file in the outputs/ directory"
    args_schema: Type[BaseModel] = ExportInput

    def _run(self, content: str, filename: str) -> str:
        """Export content to a markdown file.

        Args:
            content: The markdown content to save
            filename: The filename (without extension)

        Returns:
            Success message with file path
        """
        output_dir = "./outputs"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.md")

        with open(filepath, "w") as f:
            f.write(content)

        return f"Markdown report saved to: {filepath}"


class PDFExportTool(BaseTool):
    """Tool for exporting markdown content to professionally formatted PDF."""

    name: str = "export_pdf"
    description: str = (
        "Export markdown content to a professionally formatted PDF file. "
        "The PDF will have proper styling, headers, code blocks, and citations."
    )
    args_schema: Type[BaseModel] = ExportInput

    def _run(self, content: str, filename: str) -> str:
        """Export markdown content to a well-formatted PDF.

        Args:
            content: The markdown content to convert to PDF
            filename: The filename (without extension)

        Returns:
            Success message with file path
        """
        try:
            import markdown
        except ImportError:
            return "Error: markdown package not installed"

        output_dir = "./outputs"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.pdf")

        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=["extra", "tables", "fenced_code", "codehilite", "toc"],
        )

        # Professional CSS styling
        current_time = datetime.now().strftime("%B %d, %Y")
        styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Research Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
        }}
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #1a1a1a;
            font-size: 28pt;
            margin: 0 0 10px 0;
        }}
        .header p {{
            color: #666;
            font-size: 10pt;
            margin: 0;
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 20pt;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #2563eb;
        }}
        h2 {{
            color: #2563eb;
            font-size: 16pt;
            font-weight: bold;
            margin-top: 25px;
            margin-bottom: 12px;
        }}
        h3 {{
            color: #1e40af;
            font-size: 13pt;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 10pt;
            text-align: justify;
        }}
        ul, ol {{
            margin-bottom: 12pt;
            padding-left: 25pt;
        }}
        li {{
            margin-bottom: 6pt;
            line-height: 1.5;
        }}
        strong {{
            color: #1a1a1a;
            font-weight: bold;
        }}
        code {{
            background-color: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #dc2626;
        }}
        pre {{
            background-color: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
            border-left: 4px solid #3b82f6;
        }}
        pre code {{
            background-color: transparent;
            color: #e2e8f0;
            padding: 0;
            font-size: 9pt;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
            word-break: break-all;
        }}
        blockquote {{
            border-left: 4px solid #d1d5db;
            padding-left: 16px;
            margin-left: 0;
            color: #6b7280;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: bold;
            color: #1a1a1a;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Research Report</h1>
        <p>Generated on {current_time}</p>
    </div>
    {html_content}
</body>
</html>"""

        # Try to use WeasyPrint if available, otherwise save as HTML
        try:
            from weasyprint import HTML
            HTML(string=styled_html).write_pdf(filepath)
            return f"PDF report saved to: {filepath}"
        except (ImportError, OSError) as e:
            # WeasyPrint not available or missing dependencies
            # Save as HTML instead
            html_path = filepath.replace(".pdf", ".html")
            with open(html_path, "w") as f:
                f.write(styled_html)
            return f"PDF library not available. Professional HTML report saved to: {html_path} (You can open this in a browser and print to PDF)"
