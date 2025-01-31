"""Graph Index Creator."""
from typing import Optional, Type

from pydantic import BaseModel

from langplus.base_language import BaseLanguageModel
from langplus.chains.llm import LLMChain
from langplus.graphs.networkx_graph import NetworkxEntityGraph, parse_triples
from langplus.indexes.prompts.knowledge_triplet_extraction import (
    KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT,
)


class GraphIndexCreator(BaseModel):
    """Functionality to create graph index."""

    llm: Optional[BaseLanguageModel] = None
    graph_type: Type[NetworkxEntityGraph] = NetworkxEntityGraph

    def from_text(self, text: str) -> NetworkxEntityGraph:
        """Create graph index from text."""
        if self.llm is None:
            raise ValueError("llm should not be None")
        graph = self.graph_type()
        chain = LLMChain(llm=self.llm, prompt=KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT)
        output = chain.predict(text=text)
        knowledge = parse_triples(output)
        for triple in knowledge:
            graph.add_triple(triple)
        return graph

    async def afrom_text(self, text: str) -> NetworkxEntityGraph:
        """Create graph index from text asynchronously."""
        if self.llm is None:
            raise ValueError("llm should not be None")
        graph = self.graph_type()
        chain = LLMChain(llm=self.llm, prompt=KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT)
        output = await chain.apredict(text=text)
        knowledge = parse_triples(output)
        for triple in knowledge:
            graph.add_triple(triple)
        return graph
