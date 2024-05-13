import re
from io import BytesIO
from typing import Tuple, List
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from pypdf import PdfReader
import faiss

# Initialize Sentence Transformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define FAISS class with dynamic dimensionality
class FAISS:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)

    def build_index(self, embeddings):
        self.index.add(embeddings)

    def search(self, query_embedding, k):
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices


def parse_pdf(file: BytesIO, filename: str) -> Tuple[List[str], str]:
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
            text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
            text = re.sub(r"\n\s*\n", "\n\n", text)
            output.append(text)
    return output, filename

def text_to_docs(text: List[str], filename: str) -> List[Document]:
    if isinstance(text, str):
        text = [text]
    page_docs = [Document(page_content=page) for page in text]
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    doc_chunks = []
    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=0,
        )
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i}
            )
            doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc.metadata["filename"] = filename
            doc_chunks.append(doc)
    return doc_chunks

def docs_to_index(docs):
    embeddings = model.encode([doc.page_content for doc in docs])
    embedding_dim = embeddings.shape[1]  # Get the dimensionality of embeddings
    index = FAISS(embedding_dim)
    index.build_index(embeddings)
    return index

def get_index_for_pdf(pdf_files, pdf_names):
    documents = []
    for pdf_file, pdf_name in zip(pdf_files, pdf_names):
        text, filename = parse_pdf(BytesIO(pdf_file), pdf_name)
        docs = text_to_docs(text, filename)
        documents.extend(docs)  # Collect all documents
    
    # Create the FAISS index from these documents
    index = docs_to_index(documents)
    return documents, index  # Return both the documents and the index


def search_index(query: str, index: FAISS, documents: List[Document], top_k: int = 5):
    # Convert user message to embedding
    user_embedding = model.encode([query])
    # Search the index
    D, I = index.search(user_embedding, top_k)  # D: distances, I: indices
    # Retrieve documents and their distances
    return [(documents[i], D[0][j]) for j, i in enumerate(I[0])]

