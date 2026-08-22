import os
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class PDFExporter:
    @staticmethod
    def export(markdown_text: str, output_path: str):
        """
        Converts markdown text to a simple PDF using ReportLab.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        Story = []
        
        # Super simplified markdown parser for demo
        for line in markdown_text.split('\n'):
            line = line.strip()
            if not line:
                Story.append(Spacer(1, 12))
            elif line.startswith('# '):
                Story.append(Paragraph(line[2:], styles['Title']))
            elif line.startswith('## '):
                Story.append(Paragraph(line[3:], styles['Heading2']))
            elif line.startswith('- '):
                Story.append(Paragraph(line, styles['Normal']))
            elif line.startswith('1. ') or line.startswith('2. '):
                Story.append(Paragraph(line, styles['Normal']))
            else:
                Story.append(Paragraph(line, styles['Normal']))
                
        doc.build(Story)
        return output_path
