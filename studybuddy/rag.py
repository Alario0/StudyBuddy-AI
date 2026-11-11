"""Extração, divisão, indexação e recuperação de documentos."""
from __future__ import annotations
import io
from dataclasses import dataclass
from typing import Sequence
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

@dataclass
class UploadedFile:
    name: str
    content: bytes


def extract_documents(files: Sequence[UploadedFile]) -> list[Document]:
    documents: list[Document] = []
    for item in files:
        if item.name.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(item.content))
            for index, page in enumerate(reader.pages, start=1):
                content = (page.extract_text() or "").strip()
                if content:
                    documents.append(Document(page_content=content, metadata={"source": item.name, "page": index}))
        elif item.name.lower().endswith(".txt"):
            content = item.content.decode("utf-8-sig", errors="replace").strip()
            if content:
                documents.append(Document(page_content=content, metadata={"source": item.name, "page": None}))
        else:
            raise ValueError(f"Formato não suportado: {item.name}")
    return documents


def split_documents(documents: Sequence[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(list(documents))


def make_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


def create_index(chunks: Sequence[Document], embeddings=None):
    from langchain_community.vectorstores import FAISS
    if not chunks:
        raise ValueError("Não foi possível extrair texto dos documentos. PDFs digitalizados exigem OCR.")
    return FAISS.from_documents(list(chunks), embeddings or make_embeddings())


def retrieve(index, question: str, k: int = 4) -> list[Document]:
    return index.similarity_search(question, k=k)


def format_context(documents: Sequence[Document]) -> str:
    parts = []
    for i, doc in enumerate(documents, 1):
        page = doc.metadata.get("page")
        where = f"{doc.metadata.get('source', 'Documento')}" + (f", página {page}" if page else "")
        parts.append(f"[{i}] Fonte: {where}\n{doc.page_content}")
    return "\n\n".join(parts)


def source_labels(documents: Sequence[Document]) -> list[str]:
    return [f"[{i}] {doc.metadata.get('source', 'Documento')}" + (f" — página {doc.metadata['page']}" if doc.metadata.get('page') else "") for i, doc in enumerate(documents, 1)]
