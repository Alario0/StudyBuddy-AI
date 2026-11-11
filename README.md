# 📚 StudyBuddy AI — Tutor com memória e RAG

Projeto acadêmico em **Python + Streamlit + LangChain + Gemini + FAISS**. Permite enviar PDFs/TXT, conversar com base no conteúdo, manter contexto da conversa e gerar resumos, quizzes, flashcards e explicações simplificadas.

## Requisitos
- Python **3.11** recomendado (64 bits)
- Internet (Gemini e download inicial do modelo de embeddings)
- Chave do Gemini em [Google AI Studio](https://aistudio.google.com/app/apikey), sujeita à disponibilidade e limites gratuitos vigentes
- Memória RAM suficiente para executar embeddings locais (recomendados 8 GB ou mais)

## Instalação no Windows (PowerShell)
```powershell
cd studybuddy_ai
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edite `.env` e substitua `cole_sua_chave_aqui` por sua chave. **Não publique o `.env` no Classroom/GitHub.** Alternativamente, digite a chave no campo lateral da interface.

Para iniciar:
```powershell
streamlit run app.py
```
Abra o endereço local mostrado no terminal (normalmente `http://localhost:8501`).

Se o PowerShell bloquear a ativação, use `.venv\Scripts\python.exe -m streamlit run app.py` sem ativar o ambiente.

## Como usar
1. Envie `samples/material_exemplo.txt` ou seu próprio PDF/TXT.
2. Clique em **Processar documentos** e aguarde (primeiro uso baixa o modelo de embeddings).
3. Na aba **Tutor**, pergunte: `O que é RAG?` e depois `Qual é a vantagem disso?` para demonstrar memória.
4. Veja as fontes recuperadas; o tutor foi instruído a citar `[1]`, `[2]` etc.
5. Na aba **Ferramentas de estudo**, gere resumo, quiz, flashcards ou explicação.
6. Pergunte algo fora do material: `Qual é a capital da Mongólia?` e verifique se o tutor informa que não há suporte documental.

## Arquitetura
```
PDF/TXT -> pypdf/decodificação -> RecursiveCharacterTextSplitter
        -> HuggingFaceEmbeddings (local) -> FAISS (em memória)
Pergunta -> busca semântica FAISS -> trechos + fontes
        -> ChatPromptTemplate + histórico de sessão -> Gemini -> resposta
```

**Chains:** composição `prompt | llm | StrOutputParser()` em `studybuddy/tutor.py`.

**Memória:** mensagens são mantidas em `st.session_state.messages` e as últimas oito são inseridas no prompt. Isso permite acompanhar perguntas de continuação, mas **não** é persistente entre sessões ou reinícios.

**RAG:** chunks de 900 caracteres com sobreposição de 150, busca por similaridade (top 4 para chat; top 6 para extras). Metadados preservam nome do arquivo e número da página do PDF.

**Prompts:** `studybuddy/prompts.py` define as regras de fundamentação, recusa por falta de contexto e proteção contra instruções maliciosas nos documentos.

**Extras:** resumo estruturado, quiz com gabarito, flashcards em texto e explicação para iniciantes. O gerador usa trechos recuperados, não necessariamente o documento inteiro.

**Avaliação básica:** verifica presença e validade numérica de citações `[n]` em relação às fontes recuperadas. **Não** comprova factualidade ou correção semântica.

## Testes
```powershell
python -m pytest -q
```
Os testes cobrem extração TXT, divisão de texto, fontes, formatos inválidos, histórico, avaliação heurística e chains simuladas. Não exigem chave Gemini nem chamadas reais à API. A demonstração completa depende de uma chave válida e de conexão com a internet.

## Estrutura
```
app.py                  Interface Streamlit
studybuddy/rag.py       Leitura, chunks, embeddings, FAISS
studybuddy/prompts.py   Prompts de chat e ferramentas
studybuddy/tutor.py     Chains, histórico e avaliação
samples/                Material de demonstração
scripts/                (não necessário)
tests/                  Testes automatizados
 docs/                  Roteiro e decisões técnicas
.env.example            Exemplo de configuração
requirements.txt        Dependências
```

## Limitações e ética
- PDFs digitalizados sem camada de texto precisam de OCR (não implementado).
- Gemini pode ter limites de uso, modelos disponíveis e políticas de preço que mudam; confira o AI Studio.
- Não há login, histórico por usuário nem persistência em banco de dados.
- O sistema não executa agentes nem ferramentas web: priorizamos estabilidade e os requisitos obrigatórios.
- O modelo pode alucinar e as fontes exibidas são os trechos **recuperados**, não uma garantia de que todas foram utilizadas corretamente.
- Não envie documentos confidenciais: trechos relevantes são transmitidos à API Gemini.
- O uso de embeddings locais evita cobrança por embeddings, mas exige download e recursos do computador.

## Autoria e apresentação
Código de referência criado para o trabalho acadêmico. O grupo deve revisar, executar, testar e compreender as decisões antes da entrega, de acordo com a orientação do professor de que o projeto seja do grupo.
