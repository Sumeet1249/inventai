from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class NoveltyOutput(BaseModel):
    novelty_score: float = Field(description="Score from 0.0 to 1.0 indicating novelty. 0 means completely anticipated, 1 means completely novel.")
    gaps_found: list[str] = Field(description="Identified novel gaps not covered by prior art.")
    rejections: list[str] = Field(description="Claims or aspects that are likely anticipated by the prior art.")
    summary: str = Field(description="A brief summary of the patentability assessment.")

class NoveltyAnalysisChain:
    """
    RAG Pipeline for analyzing an idea against retrieved prior art.
    """
    def __init__(self, llm=None):
        self.llm = llm or ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        self.parser = JsonOutputParser(pydantic_object=NoveltyOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Patent Attorney and Patent Examiner.\n"
                       "Analyze the user's invention idea against the provided prior art.\n"
                       "You must output ONLY valid JSON matching the following schema:\n"
                       "{format_instructions}"),
            ("user", "Invention Idea:\n{idea}\n\nRetrieved Prior Art:\n{prior_art}\n\nPerform a novelty analysis.")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def analyze(self, idea: str, prior_art: list[dict]) -> dict:
        """Runs the RAG novelty analysis."""
        # Format prior art to a string to inject into context
        formatted_prior_art = "\n\n".join(
            [f"Title: {item.get('title')}\nAbstract: {item.get('abstract')}" for item in prior_art]
        )
        
        if not formatted_prior_art:
            formatted_prior_art = "No relevant prior art found."

        try:
            result = await self.chain.ainvoke({
                "idea": idea,
                "prior_art": formatted_prior_art,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            # Fallback on LLM failure
            return {
                "novelty_score": 0.5,
                "gaps_found": ["Unable to determine gaps due to LLM error."],
                "rejections": [],
                "summary": f"Analysis failed: {str(e)}"
            }

novelty_chain = NoveltyAnalysisChain()
