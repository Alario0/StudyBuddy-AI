"""Aplicativo Streamlit do StudyBuddy AI. Execute: streamlit run app.py"""
import os
import hashlib
import streamlit as st
from dotenv import load_dotenv
from studybuddy.rag import UploadedFile, extract_documents, split_documents, create_index
from studybuddy.tutor import make_llm, answer_question, generate_extra, evaluate_grounding

load_dotenv()
st.set_page_config(page_title="StudyBuddy AI", page_icon="📚", layout="wide")
st.markdown("""<style>
.block-container{padding-top:2rem;max-width:1250px}
.hero{background:linear-gradient(120deg,#262354,#162b49);border:1px solid #4e4b82;
border-radius:18px;padding:22px 28px;margin-bottom:18px}
.hero h1{margin:0;font-size:2.1rem}.hero p{color:#cdd6f5;margin:6px 0 0}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>📚 StudyBuddy AI</h1><p>Seu tutor pessoal com memória, documentos e inteligência artificial.</p></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "index" not in st.session_state:
    st.session_state.index = None
if "fingerprint" not in st.session_state:
    st.session_state.fingerprint = None
if "file_count" not in st.session_state:
    st.session_state.file_count = 0

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Chave da API Gemini", value=os.getenv("GOOGLE_API_KEY", ""), type="password", help="Crie gratuitamente em aistudio.google.com")
    model = st.text_input("Modelo Gemini", value=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"))
    st.divider()
    st.header("📄 Seus materiais")
    uploaded = st.file_uploader("Envie PDFs ou TXT", type=["pdf", "txt"], accept_multiple_files=True)
    if st.button("🔎 Processar documentos", use_container_width=True, disabled=not uploaded):
        files = [UploadedFile(name=f.name, content=f.getvalue()) for f in uploaded]
        digest = hashlib.sha256(b"".join(f.name.encode() + f.content for f in files)).hexdigest()
        if digest != st.session_state.fingerprint:
            try:
                with st.spinner("Extraindo texto, criando embeddings e indexando... Na primeira execução o modelo local será baixado."):
                    docs = extract_documents(files)
                    chunks = split_documents(docs)
                    index = create_index(chunks)
                st.session_state.index = index
                st.session_state.fingerprint = digest
                st.session_state.file_count = len(files)
                st.session_state.messages = []
                st.success(f"{len(files)} arquivo(s) e {len(chunks)} trecho(s) indexados!")
            except Exception as exc:
                st.error(f"Falha ao processar documentos: {exc}")
        else:
            st.info("Esses documentos já foram processados.")
    st.caption(f"Materiais ativos: {st.session_state.file_count}")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Os documentos e a conversa ficam apenas na sessão atual. Não envie dados sigilosos à API.")

chat_tab, tools_tab, about_tab = st.tabs(["💬 Tutor", "🧠 Ferramentas de estudo", "ℹ️ Sobre"])
with chat_tab:
    if st.session_state.index is None:
        st.info("Comece enviando um PDF ou TXT na barra lateral e clique em 'Processar documentos'.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📌 Trechos consultados — fontes recuperadas"):
                    for src in msg["sources"]:
                        st.write(src)
    question = st.chat_input("Pergunte algo sobre seu material...", disabled=st.session_state.index is None)
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        if not api_key or api_key == "cole_sua_chave_aqui":
            st.error("Configure a chave gratuita do Gemini na barra lateral ou no arquivo .env.")
        else:
            try:
                with st.spinner("Consultando os documentos..."):
                    llm = make_llm(api_key, model)
                    result = answer_question(llm, st.session_state.index, question, st.session_state.messages)
                st.session_state.messages.extend([{"role": "user", "content": question}, {"role": "assistant", "content": result["answer"], "sources": result["sources"]}])
                with st.chat_message("assistant"):
                    st.markdown(result["answer"])
                    with st.expander("📌 Fontes e avaliação básica"):
                        for src in result["sources"]:
                            st.write(src)
                        st.json(evaluate_grounding(result["answer"], result["sources"]))
            except Exception as exc:
                st.error(f"Não foi possível consultar o Gemini: {exc}. Verifique a chave, o modelo e os limites gratuitos.")

with tools_tab:
    st.subheader("Transforme seus documentos em material de revisão")
    tool = st.selectbox("Escolha uma ferramenta", ["Resumo estruturado", "Quiz com gabarito", "Flashcards", "Explicação para iniciantes"])
    topic = st.text_input("Tema específico (opcional)", placeholder="Ex.: redes neurais, fotossíntese, capítulo 2")
    tasks = {
        "Resumo estruturado": "Crie um resumo organizado com tópicos, definições e 3 ideias centrais.",
        "Quiz com gabarito": "Crie 5 perguntas de múltipla escolha com 4 alternativas cada, e gabarito comentado ao final.",
        "Flashcards": "Crie 8 flashcards no formato 'Frente: ... / Verso: ...', objetivos e curtos.",
        "Explicação para iniciantes": "Explique o assunto como se eu tivesse 10 anos, com analogias simples e um exemplo do material.",
    }
    if st.button("✨ Gerar material", type="primary", disabled=st.session_state.index is None):
        if not api_key or api_key == "cole_sua_chave_aqui":
            st.warning("Informe a chave do Gemini primeiro.")
        else:
            try:
                with st.spinner("Preparando material..."):
                    result = generate_extra(make_llm(api_key, model), st.session_state.index,
                                            tasks[tool] + (f" Tema: {topic}." if topic else ""),
                                            query=topic or "conceitos principais do material")
                st.markdown(result["answer"])
                st.download_button("⬇️ Baixar como texto", data=result["answer"], file_name="studybuddy_material.txt", mime="text/plain")
                with st.expander("Fontes recuperadas"):
                    for src in result["sources"]:
                        st.write(src)
            except Exception as exc:
                st.error(f"Erro ao gerar material: {exc}")

with about_tab:
    st.markdown("""### Como funciona
1. O texto dos PDFs/TXT é extraído e dividido em trechos.
2. Um modelo de embeddings multilíngue transforma trechos em vetores.
3. O FAISS encontra os trechos semanticamente próximos à pergunta.
4. Uma chain do LangChain envia contexto, histórico e pergunta ao Gemini.
5. O tutor responde com citações e mostra as fontes recuperadas.

**Privacidade:** arquivos e índice são mantidos em memória na sessão do Streamlit; os trechos recuperados são enviados ao serviço Gemini. Não há armazenamento permanente de histórico nem autenticação de usuários.

**Limitações:** PDFs escaneados sem texto exigem OCR; o modelo pode cometer erros; a checagem de citações é heurística e não comprova a veracidade da resposta.""")
