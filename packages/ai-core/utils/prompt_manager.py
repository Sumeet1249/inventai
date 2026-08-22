import os
from jinja2 import Environment, FileSystemLoader

class PromptManager:
    """
    Loads and renders LLM prompts using Jinja2 templates.
    Allows decoupling of complex prompt engineering from Python code.
    """
    def __init__(self, templates_dir: str = "prompts"):
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def get_prompt(self, template_name: str, **kwargs) -> str:
        """
        Renders a template with the provided kwargs.
        """
        template = self.env.get_template(f"{template_name}.jinja")
        return template.render(**kwargs)
