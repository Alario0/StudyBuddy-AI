from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from studybuddy.tutor import format_history, evaluate_grounding, answer_question, generate_extra

def test_memory_format():
    history = [{'role':'user','content':'O que é RAG?'}, {'role':'assistant','content':'Recuperação aumentada.'}]
    assert 'O que é RAG?' in format_history(history)
    assert 'Recuperação aumentada.' in format_history(history)

def test_grounding_heuristic():
    result = evaluate_grounding('Afirmação [1] e outra [9].', ['[1] livro.pdf'])
    assert result['citacoes_validas'] == 1
    assert result['citacoes_invalidas'] == 1

def test_rag_chain_with_fake_llm():
    fake_llm = RunnableLambda(lambda prompt: 'A resposta está no texto [1].')
    docs = [Document(page_content='RAG recupera documentos.', metadata={'source':'a.txt','page':None})]
    with patch('studybuddy.tutor.retrieve', return_value=docs):
        # RunnableLambda returns string; StrOutputParser accepts text output.
        result = answer_question(fake_llm, object(), 'O que é RAG?', [])
    assert '[1]' in result['answer']
    assert 'a.txt' in result['sources'][0]

def test_extra_chain_with_fake_llm():
    fake_llm = RunnableLambda(lambda prompt: 'Resumo: recuperação de informação.')
    docs = [Document(page_content='RAG recupera documentos.', metadata={'source':'a.txt'})]
    with patch('studybuddy.tutor.retrieve', return_value=docs):
        result = generate_extra(fake_llm, object(), 'Resuma')
    assert result['answer'].startswith('Resumo')
