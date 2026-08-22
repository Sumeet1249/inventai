import jinja2

class DocumentComposer:
    """
    Composes raw artifact data into structured Markdown documents.
    """
    PATENT_TEMPLATE = """# Patent Draft
    
## Title
{{ title }}

## Abstract
A novel architecture for a {{ title.lower() }}, specifically designed with unique novelty: {{ patent_data.novelty }}.

## Background & Prior Art
The invention overcomes limitations found in existing prior art, notably bypassing constraints in {{ patent_data.prior_art_citations | join(', ') }}.

## Detailed Description
The structural body is constructed from {{ physics_assets.material }}.
Key research inputs:
{% for finding in research_data.key_findings %}
- {{ finding }}
{% endfor %}

## Claims
1. An apparatus comprising a foldable frame capable of 40cm span.
2. The apparatus of claim 1, constructed using {{ physics_assets.material }}.
"""

    ENGINEERING_TEMPLATE = """# Engineering Validation Report

## System Overview
{{ title }}

## Material & Manufacturing
- **Material Selection**: {{ physics_assets.material }}

## Computational Physics Simulation
- **Max Von Mises Stress**: {{ physics_assets.max_stress_mpa }} MPa
- **Calculated Safety Factor**: {{ physics_assets.safety_factor }}
- **Assessment**: {% if physics_assets.safety_factor >= 1.5 %}SAFE{% else %}UNSAFE{% endif %}

## Attached CAD Assets
- STEP: {{ cad_assets.step }}
- STL: {{ cad_assets.stl }}
"""

    @staticmethod
    def compose_patent_draft(data: dict) -> str:
        template = jinja2.Template(DocumentComposer.PATENT_TEMPLATE)
        return template.render(**data)

    @staticmethod
    def compose_engineering_report(data: dict) -> str:
        template = jinja2.Template(DocumentComposer.ENGINEERING_TEMPLATE)
        return template.render(**data)
