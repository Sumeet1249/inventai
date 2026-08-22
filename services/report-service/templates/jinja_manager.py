class JinjaManager:
    """
    Manages Jinja2 templates for mapping raw JSON into Markdown/HTML.
    """
    @staticmethod
    def render_markdown(template_name: str, data: dict) -> str:
        # Mock template rendering
        title = data.get("name", "Untitled Invention")
        description = data.get("description", "")
        
        return f"""# Invention Report: {title}
        
## Overview
{description}

## Patent Claims
1. A method for autonomous operation as described...

## Physical Validation
Safety Factor: 1.5 (Pass)
"""
