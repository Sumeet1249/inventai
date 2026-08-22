import os

class PDFExporter:
    """
    Adapter for ReportLab to convert Markdown/HTML into PDF.
    """
    @staticmethod
    def export(markdown_content: str, filename: str) -> str:
        # Mock implementation. In reality, parse markdown to ReportLab Flowables.
        out_path = f"/tmp/{filename}.pdf"
        return out_path
