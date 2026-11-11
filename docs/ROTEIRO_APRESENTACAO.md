# Roteiro oral — 5 a 8 minutos

## 0:00–0:45 — Abertura (Integrante 1)
"Nosso projeto é o StudyBuddy AI, um tutor que responde com base nos materiais do aluno. O problema que buscamos resolver é a dificuldade de localizar respostas em PDFs extensos e transformar conteúdo em revisão prática."

## 0:45–2:00 — Arquitetura (Integrante 2)
"Quando enviamos um documento, extraímos o texto e dividimos em trechos com sobreposição. O modelo multilíngue transforma os trechos em embeddings e o FAISS faz busca semântica. Esse processo é RAG: recuperar conteúdo antes de pedir uma resposta ao Gemini."

## 2:00–3:15 — Demonstração do RAG (Integrante 3)
1. Abra o aplicativo já instalado e com chave configurada.
2. Envie `samples/material_exemplo.txt`, clique em processar.
3. Pergunte: **O que é RAG?**
4. Expanda as fontes recuperadas e mostre os nomes dos documentos.
5. Pergunte: **Qual é a vantagem disso?** — explique que o histórico ajuda a interpretar "disso".

## 3:15–4:40 — Ferramentas extras (Integrante 4)
"Implementamos quatro extras: resumo, quiz com gabarito, flashcards e explicação para iniciantes. Eles reutilizam a recuperação documental, evitando pedir respostas genéricas sem contexto." Demonstre **Quiz com gabarito** e **Resumo estruturado**.

## 4:40–5:50 — Chains, prompts e memória (Integrante 2)
"Uma chain do LangChain combina prompt, modelo Gemini e parser de texto. O prompt instrui o modelo a usar somente o contexto, a citar trechos e a declarar falta de informação. A memória é mantida na sessão Streamlit e as últimas oito mensagens entram no prompt."

## 5:50–6:45 — Testes e limitações (Integrante 5)
"Criamos testes para extração, chunks, fontes, memória e fluxo das chains com modelos simulados. Também verificamos se as citações referem-se a fontes recuperadas. Reconhecemos que a avaliação é heurística e que PDFs escaneados exigiriam OCR." Execute `python -m pytest -q` se o ambiente estiver preparado.

## 6:45–7:30 — Encerramento (Integrante 1)
"O diferencial é integrar RAG, memória e ferramentas de estudo em uma única interface. Priorizamos a confiabilidade da demonstração e uma arquitetura modular, preparada para futuras melhorias, como histórico persistente e agentes."

## Perguntas prováveis do professor
**O que é RAG?** Recuperar trechos relevantes e incluí-los no prompt do modelo para fundamentar a resposta.

**Por que FAISS?** Busca vetorial eficiente, simples de executar localmente e adequada para demonstração.

**Onde está a memória?** `st.session_state.messages`, com as últimas oito mensagens passadas ao prompt.

**O que é uma chain?** Composição de etapas `prompt | llm | parser` usando LangChain.

**O Gemini faz embeddings?** Não neste projeto. Os embeddings são locais com Sentence Transformers; Gemini gera as respostas.

**O que acontece se não houver resposta no PDF?** O prompt orienta a declarar falta de informação, embora isso não seja garantia absoluta.

**Por que não tem agentes?** Agentes eram opcionais; priorizamos requisitos mínimos e testes.

## Checklist antes da aula
- [ ] Instalar dependências e validar versão do Python.
- [ ] Configurar chave válida no `.env` (não apresentar a chave na tela).
- [ ] Processar arquivo de exemplo com antecedência para baixar embeddings.
- [ ] Testar chat, pergunta de continuação, resumo e quiz com internet.
- [ ] Rodar testes automatizados e conferir resultados.
- [ ] Definir quem fala cada parte e ensaiar cronometrado.
- [ ] Preparar capturas de tela de reserva se a internet falhar.
