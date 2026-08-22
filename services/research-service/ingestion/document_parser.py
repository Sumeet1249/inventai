import fitz  # PyMuPDF
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from typing import List, Dict, Any
import os

class DocumentParser:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def parse_pdf(self, file_path: str, metadata: Dict[str, Any] = None) -> List[Document]:
        metadata = metadata or {}
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            
        llama_doc = Document(text=text, metadata=metadata)
        nodes = self.node_parser.get_nodes_from_documents([llama_doc])
        return nodes
