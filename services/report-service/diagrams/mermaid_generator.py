class MermaidGenerator:
    """
    Converts graph relations or workflow timelines into Mermaid markdown syntax.
    """
    @staticmethod
    def generate_workflow_chart(steps: list) -> str:
        chart = "```mermaid\\ngraph TD\\n"
        for i in range(len(steps) - 1):
            chart += f"  {steps[i]} --> {steps[i+1]}\\n"
        chart += "```"
        return chart
