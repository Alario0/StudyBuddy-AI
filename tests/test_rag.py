from studybuddy.rag import UploadedFile, extract_documents, split_documents, format_context, source_labels
from langchain_core.documents import Document

def test_txt_extract():
    docs = extract_documents([UploadedFile('a.txt', 'Olá mundo'.encode())])
    assert docs[0].page_content == 'Olá mundo'
    assert docs[0].metadata['source'] == 'a.txt'

def test_split_and_sources():
    chunks = split_documents([Document(page_content='Redes neurais aprendem padrões. ' * 100, metadata={'source':'a.txt', 'page':None})])
    assert len(chunks) > 1
    assert '[1]' in format_context(chunks[:1])
    assert 'a.txt' in source_labels(chunks[:1])[0]

def test_unsupported():
    import pytest
    with pytest.raises(ValueError):
        extract_documents([UploadedFile('a.docx', b'abc')])
