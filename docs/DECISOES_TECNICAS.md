# Decisões técnicas

| Componente | Escolha | Justificativa |
|---|---|---|
| Interface | Streamlit | Aplicação web em Python sem frontend separado |
| LLM | Gemini via LangChain | Integração simples; pode haver cota gratuita |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 | Multilíngue e local, sem custo por requisição |
| Vetores | FAISS em memória | Busca rápida e instalação simples |
| Documentos | pypdf + TXT | PDF prioritário; extrai texto de PDFs digitais |
| Chunking | 900/150 | Equilíbrio entre contexto e granularidade |
| Memória | Streamlit session_state | Contexto de conversa por sessão, sem banco de dados |
| Chains | LCEL prompt/LLM/parser | Demonstra explicitamente conceito de chain |
| Testes | pytest e fake LLM | Reprodutíveis, sem depender da API |

## Fluxo de dados
Upload -> extração -> chunks -> embeddings -> índice FAISS -> busca top-k -> prompt com histórico e trechos -> Gemini -> resposta e fontes.

## Riscos e melhorias
1. **PDF escaneado:** implementar OCR.
2. **Sessões não persistentes:** adicionar SQLite e autenticação.
3. **Fontes insuficientes:** usar limiar de similaridade e reranking.
4. **Alucinação:** implementar avaliação de groundedness por LLM e testes de perguntas sem resposta.
5. **Custos/limites:** monitorar cotas gratuitas do provedor.
