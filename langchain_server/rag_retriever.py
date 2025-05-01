import os
import json
import re
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter



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


class RAGHelper:
    def __init__(self):
        self.fpath = "../testing/ucs_website.json"
        self.persist_directory = "rag/chroma_db"
        self.topk = 1
        self.data = self.load_json()
        self.index_to_chroma() # Index once

    def load_json(self):
        # Load JSON file into a Python dictionary.
        if not os.path.exists(self.fpath):
            raise FileNotFoundError(f"JSON file not found at {self.fpath}")

        with open(self.fpath, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize_text(self, txt):
        # Clean text by removing escape characters and extra whitespace.
        for c in ['\r', '\n']:
            txt = txt.replace(c, ' ')
        
        txt = re.sub(r'\s+', ' ', txt)

        return txt.strip()

    def convert_to_documents(self):
        # Convert the loaded JSON into a list of LangChain Document objects.
        documents = []

        # Top-level sections like counselling, appointment, etc.
        for section_key, content in self.data.items():
            if section_key in ["url", "appointment_link"]:
                continue
            
            title = content.get("title", "")
            section_text = content.get("section", "")
            full_text = f"{title}\n{section_text}"
            normalized = self.normalize_text(full_text)
            
            documents.append(Document(
                page_content=normalized,
                metadata={"source_section": section_key, "title": title}
            ))

        return documents

    def index_to_chroma(self):
        # Split documents and index them into ChromaDB vector store.
        documents = self.convert_to_documents()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=OpenAIEmbeddings(),
            persist_directory=self.persist_directory
        )

        return vectorstore

    def retrieve(self, query):
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=OpenAIEmbeddings()
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": self.topk})
        retrieved_docs = retriever.invoke(query)

        # Build structured context
        context_blocks = []

        for doc in retrieved_docs:
            title = doc.metadata.get("title", "Untitled Section")
            text = doc.page_content.strip()
            block = f"{title}:\n{text}"
            context_blocks.append(block)
        
        context = "\n".join(context_blocks)

        # rag_prompt = """
        # You have access to the following structured information extracted from NUS's University Counselling Services website. The content is grouped into titled sections:

        # {context}

        # A user has asked the following question:

        # "{question}"

        # Your task is to:

        # 1. Provide a clear, concise, and empathetic answer to the user's question.
        # 2. For each section in the context, briefly explain how it is relevant (or not) to answering the user's concern.
        # 3. Extract and list **all** helpful contact information such as phone numbers, email addresses, appointment links, app names, or physical addresses mentioned in the context.
        # 4. Organize your response bullet points to ensure readability.

        # Ensure your tone is kind and understanding. Where multiple resources exist, sort your response according to the most appropriate one at the top for their described issue. If there are repeat information, do not repeat, show unique values.

        # Helpful and Empathetic Answer:
        # """

        # final_prompt = rag_prompt.format(context=context, question=query)
        
        return context
    