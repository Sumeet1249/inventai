import os

class DOCXExporter:
    """
    Adapter for python-docx to convert Markdown/HTML into DOCX.
    """
    @staticmethod
    def export(markdown_content: str, filename: str) -> str:
        # Mock implementation.
        out_path = f"/tmp/{filename}.docx"
        return out_path
