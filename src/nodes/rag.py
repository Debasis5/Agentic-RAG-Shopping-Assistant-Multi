import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.state import GraphState

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")

_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

_vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=_embeddings,
    collection_name="support_docs",
)

_retriever = _vectorstore.as_retriever(search_kwargs={"k": 3})


def rag_node(state: GraphState) -> dict:
    query = state["query"]
    docs = _retriever.invoke(query)
    retrieved = [
        f"[Source: {doc.metadata.get('title', 'Unknown')}]\n{doc.page_content}"
        for doc in docs
    ]
    print(f"[rag] retrieved {len(retrieved)} chunks for query: {query!r}")
    for i, doc in enumerate(docs, 1):
        print(f"  [{i}] {doc.metadata.get('title', '?')} | {doc.page_content[:60]!r}...")
    return {"retrieved_docs": retrieved}
