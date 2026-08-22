from jinja2 import Environment, FileSystemLoader
from langchain_core.prompts import PromptTemplate as LangchainPromptTemplate

class PromptManager:
    """
    Enterprise Prompt Manager. Loads templates via Jinja2 and 
    converts them into LangChain PromptTemplates.
    """
    def __init__(self, templates_dir: str = "prompts"):
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def get_raw_template(self, template_name: str, **kwargs) -> str:
        template = self.env.get_template(f"{template_name}.jinja")
        return template.render(**kwargs)

    def get_langchain_prompt(self, template_name: str, input_variables: list) -> LangchainPromptTemplate:
        """
        Creates a LangChain PromptTemplate from a Jinja file.
        Assumes the jinja file is just a string template if variables are not passed immediately.
        """
        with open(f"prompts/{template_name}.jinja", "r") as f:
            template_str = f.read()
        return LangchainPromptTemplate(template=template_str, input_variables=input_variables)
