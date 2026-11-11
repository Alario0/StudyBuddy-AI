"""Chains do tutor e memória conversacional explícita por sessão."""
from __future__ import annotations
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from .prompts import RAG_PROMPT, EXTRA_PROMPT
from .rag import retrieve, format_context, source_labels


def make_llm(api_key: str, model: str = "gemini-3.5-flash-lite"):
    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.2, max_retries=0)


def format_history(messages: list[dict], limit: int = 8) -> str:
    relevant = messages[-limit:]
    return "\n".join(f"{'Aluno' if m['role'] == 'user' else 'Tutor'}: {m['content']}" for m in relevant) or "Sem mensagens anteriores."


def answer_question(llm, index, question: str, history: list[dict]) -> dict:
    docs = retrieve(index, question)
    if not docs:
        return {"answer": "Não encontrei conteúdo relevante nos documentos.", "sources": []}
    chain = RAG_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"history": format_history(history), "context": format_context(docs), "question": question})
    return {"answer": answer, "sources": source_labels(docs)}


def generate_extra(llm, index, task: str, query: str = "conceitos principais e definições") -> dict:
    docs = retrieve(index, query, k=6)
    if not docs:
        return {"answer": "Não há material disponível.", "sources": []}
    chain = EXTRA_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": format_context(docs), "task": task})
    return {"answer": answer, "sources": source_labels(docs)}


def evaluate_grounding(answer: str, sources: list[str]) -> dict:
    """Checagem heurística de rastreabilidade; não mede fidelidade semântica."""
    import re
    cited = sorted(set(int(x) for x in re.findall(r"\[(\d+)\]", answer)))
    valid = [i for i in cited if 1 <= i <= len(sources)]
    return {"fontes_recuperadas": len(sources), "citacoes_validas": len(valid), "citacoes_invalidas": len(cited) - len(valid), "tem_citacao": bool(valid)}
