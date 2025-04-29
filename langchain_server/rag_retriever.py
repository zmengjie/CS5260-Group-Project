import os

class RAGRetriever:
    def __init__(self, kb_folder="Database/knowledge_base"):
        self.kb_folder = kb_folder
        self.documents = self._load_documents()

    def _load_documents(self):
        docs = []
        for filename in os.listdir(self.kb_folder):
            if filename.endswith(".txt"):
                with open(os.path.join(self.kb_folder, filename), "r", encoding="utf-8") as f:
                    docs.append(f.read())
        return docs

    def retrieve(self, query) -> str:
        """
        Very simple keyword-based retrieval
        """
        relevant = []
        for doc in self.documents:
            if any(keyword.lower() in doc.lower() for keyword in query.lower().split()):
                relevant.append(doc)
        # Limit response to top 1 or 2 chunks for now
        return "\n\n".join(relevant[:2]) if relevant else "No relevant info found."
