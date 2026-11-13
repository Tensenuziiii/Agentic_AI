def retrieve(paper, query: str, k: int = 5):
    return paper.vectorstore.similarity_search(query, k=k, filter={"doc_id": paper.doc_id})
