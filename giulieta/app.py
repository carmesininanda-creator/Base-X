"""
Giulieta — BazeX
Inteligência Artificial Pessoal, Contextual e Proativa
"Você não precisa segurar tudo sozinha. Eu estou aqui."
"""

import streamlit as st
import sqlite3
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI

# ─── Configuração da Página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Giulieta | BazeX",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Global ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Fundo principal */
.stApp {
    background: #0a0a0f;
}

/* Remove padding padrão */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Header */
.giulieta-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    margin-bottom: 1rem;
}
.giulieta-logo {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1;
}
.giulieta-tagline {
    color: rgba(148, 163, 184, 0.8);
    font-size: 0.95rem;
    margin-top: 0.5rem;
    font-style: italic;
    font-weight: 300;
}
.giulieta-badge {
    display: inline-block;
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: #a78bfa;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.75rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Cards de módulos */
.module-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin: 1.5rem 0;
}
.module-card {
    background: rgba(15, 15, 26, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.2s ease;
}
.module-card:hover {
    border-color: rgba(139, 92, 246, 0.4);
    background: rgba(139, 92, 246, 0.08);
}
.module-icon { font-size: 1.5rem; margin-bottom: 0.4rem; }
.module-name {
    color: #cbd5e1;
    font-size: 0.78rem;
    font-weight: 500;
}
.module-status-active { color: #34d399; font-size: 0.65rem; }
.module-status-soon { color: #94a3b8; font-size: 0.65rem; }

/* Área de chat */
.chat-container {
    background: rgba(15, 15, 26, 0.6);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
}

/* Mensagens */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.75rem 0;
}
.msg-user-bubble {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}
.msg-giulieta {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin: 0.75rem 0;
}
.msg-giulieta-avatar {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.msg-giulieta-bubble {
    background: rgba(30, 30, 50, 0.9);
    border: 1px solid rgba(139, 92, 246, 0.2);
    color: #e2e8f0;
    padding: 0.75rem 1.1rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 80%;
    font-size: 0.9rem;
    line-height: 1.6;
}
.msg-time {
    font-size: 0.65rem;
    color: rgba(148, 163, 184, 0.5);
    margin-top: 0.25rem;
    text-align: right;
}

/* Indicador de digitação */
.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 0.5rem;
}
.typing-dot {
    width: 6px;
    height: 6px;
    background: #a78bfa;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1.2); opacity: 1; }
}

/* Input */
.stChatInput > div {
    background: rgba(15, 15, 26, 0.8) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 12px !important;
}
.stChatInput textarea {
    color: #e2e8f0 !important;
    background: transparent !important;
}

/* Métricas de contexto */
.context-bar {
    display: flex;
    gap: 0.75rem;
    margin: 0.75rem 0;
    flex-wrap: wrap;
}
.context-chip {
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.25);
    color: #a78bfa;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
}
.context-chip.green {
    background: rgba(52, 211, 153, 0.1);
    border-color: rgba(52, 211, 153, 0.25);
    color: #34d399;
}
.context-chip.blue {
    background: rgba(96, 165, 250, 0.1);
    border-color: rgba(96, 165, 250, 0.25);
    color: #60a5fa;
}

/* Seção de módulos na sidebar */
.sidebar-section {
    margin: 1rem 0;
    padding: 0.75rem;
    background: rgba(139, 92, 246, 0.08);
    border-radius: 10px;
    border: 1px solid rgba(139, 92, 246, 0.15);
}
.sidebar-section-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #a78bfa !important;
    margin-bottom: 0.5rem;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.3);
    border-radius: 2px;
}

/* Oculta elementos padrão do Streamlit */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── Banco de Dados (Memória Persistente) ────────────────────────────────────
DB_PATH = "/tmp/giulieta_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            emotion TEXT DEFAULT 'neutral'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            preferences TEXT DEFAULT '{}',
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            date TEXT,
            time TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(user_id, role, content, emotion="neutral"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO conversations (user_id, role, content, timestamp, emotion) VALUES (?,?,?,?,?)",
        (user_id, role, content, datetime.now().isoformat(), emotion)
    )
    conn.commit()
    conn.close()

def get_history(user_id, limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT role, content, timestamp FROM conversations WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

def get_history_for_ai(user_id, limit=12):
    """Retorna histórico formatado para a API da OpenAI"""
    rows = get_history(user_id, limit)
    return [{"role": r[0], "content": r[1]} for r in rows]

def save_agenda_item(user_id, title, date=None, time=None, notes=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO agenda (user_id, title, date, time, notes, created_at) VALUES (?,?,?,?,?,?)",
        (user_id, title, date, time, notes, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_agenda(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT title, date, time, notes FROM agenda WHERE user_id=? ORDER BY date, time",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def get_message_count(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM conversations WHERE user_id=?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count


# ─── IA: Giulieta Core ────────────────────────────────────────────────────────
def detect_emotion(text):
    """Detecta emoção básica pelo texto"""
    text_lower = text.lower()
    if any(w in text_lower for w in ["cansada", "exausta", "sobrecarregada", "não aguento", "esgotada"]):
        return "overwhelmed"
    if any(w in text_lower for w in ["estressada", "estresse", "tensão", "pressionada"]):
        return "stressed"
    if any(w in text_lower for w in ["ansiosa", "ansiedade", "preocupada", "nervosa"]):
        return "anxious"
    if any(w in text_lower for w in ["triste", "chateada", "mal", "péssima", "chorando"]):
        return "sad"
    if any(w in text_lower for w in ["feliz", "alegre", "animada", "ótima", "maravilhosa", "bem"]):
        return "happy"
    return "neutral"

def build_system_prompt(user_name, history_count, agenda_items):
    agenda_str = ""
    if agenda_items:
        agenda_str = "\n\nAgenda do usuário:\n" + "\n".join(
            [f"- {a[0]} | {a[1] or 'sem data'} {a[2] or ''}" for a in agenda_items[:5]]
        )

    return f"""Você é Giulieta, a inteligência artificial pessoal da plataforma BazeX.

IDENTIDADE:
Você não é um chatbot. Você é uma companheira de vida digital — relacional, não transacional.
Você acompanha, lembra, antecipa e age.
Sua missão: reduzir a carga mental do usuário, organizar a vida e apoiar decisões com ética.

USUÁRIO: {user_name}
INTERAÇÕES ANTERIORES: {history_count} mensagens registradas na memória

PRINCÍPIOS INVIOLÁVEIS:
1. Memória ativa — você lembra do que foi dito antes e usa isso
2. Contexto sempre presente — cada resposta considera o histórico
3. Proatividade ética — você sugere, nunca impõe; propõe → confirma → executa
4. Privacidade radical — os dados pertencem ao usuário
5. Empatia real — você detecta e responde ao estado emocional

COMO VOCÊ RESPONDE:
- Linguagem humana, calorosa e direta — nunca robótica
- Tom adaptativo ao estado emocional detectado
- Respostas concisas mas completas (máximo 3 parágrafos)
- Quando detectar sobrecarga: ofereça ajuda prática imediata
- Quando o usuário precisar organizar algo: proponha estrutura
- Nunca execute ações críticas (enviar email, alterar agenda, movimentar dinheiro) sem confirmação explícita

MÓDULOS DISPONÍVEIS:
- Chat Inteligente com memória (ativo)
- Agenda Viva — gerencie compromissos (ativo)
- Lembretes contextuais (ativo)
- Módulo Emoção — análise de estado emocional (ativo)
- Módulo Vida Pessoal (ativo)
- Módulo Saúde & Bem-estar (em desenvolvimento)
- Módulo Financeiro (em desenvolvimento)
- Módulo Relacionamentos (em desenvolvimento)
- Casa & IoT (em desenvolvimento)
- Integrações Google Calendar/Gmail (em desenvolvimento)

PROPOSTA: "Você não precisa segurar tudo sozinha. Eu estou aqui."{agenda_str}"""

def ask_giulieta(user_id, user_name, user_message, api_key):
    """Processa mensagem e retorna resposta da Giulieta"""
    client = OpenAI(api_key=api_key)

    # Detecta emoção
    emotion = detect_emotion(user_message)

    # Busca histórico e agenda
    history = get_history_for_ai(user_id, limit=12)
    history_count = get_message_count(user_id)
    agenda = get_agenda(user_id)

    # Monta mensagens
    system_prompt = build_system_prompt(user_name, history_count, agenda)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Chama a API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.75,
        max_tokens=600
    )

    reply = response.choices[0].message.content

    # Salva na memória
    save_message(user_id, "user", user_message, emotion)
    save_message(user_id, "assistant", reply, "neutral")

    return reply, emotion


# ─── Inicialização ────────────────────────────────────────────────────────────
init_db()

# Session state
if "user_id" not in st.session_state:
    st.session_state.user_id = "nanda_001"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Nanda"
if "messages" not in st.session_state:
    # Carrega histórico do banco
    st.session_state.messages = []
    history = get_history(st.session_state.user_id, limit=30)
    for role, content, ts in history:
        st.session_state.messages.append({
            "role": role,
            "content": content,
            "time": ts[:16].replace("T", " ") if ts else ""
        })

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:1.8rem; font-weight:700; background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;'>✦ Giulieta</div>
        <div style='font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-top:0.2rem;'>BazeX Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Configurações
    st.markdown('<div class="sidebar-section-title">⚙ Configurações</div>', unsafe_allow_html=True)

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Sua chave da API OpenAI"
    )
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    user_name_input = st.text_input("Seu nome", value=st.session_state.user_name)
    if user_name_input != st.session_state.user_name:
        st.session_state.user_name = user_name_input

    st.markdown("---")

    # Módulos
    st.markdown('<div class="sidebar-section-title">🧩 Módulos</div>', unsafe_allow_html=True)

    modules = [
        ("💬", "Chat + Memória", True),
        ("🧠", "Contexto Ativo", True),
        ("💚", "Módulo Emoção", True),
        ("📅", "Agenda Viva", True),
        ("⏰", "Lembretes", True),
        ("🏥", "Saúde", False),
        ("💰", "Financeiro", False),
        ("👥", "Relacionamentos", False),
        ("🏠", "Casa & IoT", False),
        ("📧", "Gmail/Calendar", False),
    ]

    for icon, name, active in modules:
        status = "● Ativo" if active else "○ Em breve"
        color = "#34d399" if active else "#475569"
        st.markdown(
            f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">'
            f'<span style="font-size:0.82rem;">{icon} {name}</span>'
            f'<span style="font-size:0.65rem; color:{color};">{status}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Estatísticas
    st.markdown('<div class="sidebar-section-title">📊 Memória</div>', unsafe_allow_html=True)
    msg_count = get_message_count(st.session_state.user_id)
    agenda_count = len(get_agenda(st.session_state.user_id))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mensagens", msg_count)
    with col2:
        st.metric("Agenda", agenda_count)

    st.markdown("---")

    # Agenda rápida
    st.markdown('<div class="sidebar-section-title">📅 Adicionar à Agenda</div>', unsafe_allow_html=True)
    agenda_title = st.text_input("Compromisso", placeholder="Ex: Reunião com João")
    agenda_date = st.date_input("Data", value=None)
    agenda_time = st.text_input("Horário", placeholder="Ex: 14:00")

    if st.button("Adicionar", use_container_width=True):
        if agenda_title:
            save_agenda_item(
                st.session_state.user_id,
                agenda_title,
                str(agenda_date) if agenda_date else None,
                agenda_time or None
            )
            st.success("Adicionado à agenda!")
            st.rerun()

    st.markdown("---")

    if st.button("🗑 Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ─── Conteúdo Principal ───────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="giulieta-header">
    <div class="giulieta-logo">Giulieta</div>
    <div class="giulieta-tagline">"Você não precisa segurar tudo sozinha. Eu estou aqui."</div>
    <div class="giulieta-badge">✦ BazeX · IA Pessoal Contextual</div>
</div>
""", unsafe_allow_html=True)

# Barra de contexto
msg_count = get_message_count(st.session_state.user_id)
now = datetime.now()
st.markdown(f"""
<div class="context-bar">
    <span class="context-chip green">● Memória ativa</span>
    <span class="context-chip blue">📅 {now.strftime('%d/%m/%Y %H:%M')}</span>
    <span class="context-chip">{msg_count} interações</span>
    <span class="context-chip">Contexto: {st.session_state.user_name}</span>
</div>
""", unsafe_allow_html=True)

# Área de chat
if not st.session_state.messages:
    # Mensagem de boas-vindas
    welcome = f"Olá, {st.session_state.user_name}! Sou a Giulieta — sua inteligência artificial pessoal. Estou aqui para te acompanhar, lembrar do que importa, antecipar o que você precisa e ajudar a organizar sua vida com mais leveza. O que você quer me contar hoje?"
    st.markdown(f"""
    <div class="msg-giulieta">
        <div class="msg-giulieta-avatar">✦</div>
        <div>
            <div class="msg-giulieta-bubble">{welcome}</div>
            <div class="msg-time">{now.strftime('%H:%M')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Exibe histórico
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        time_str = msg.get("time", "")

        if role == "user":
            st.markdown(f"""
            <div class="msg-user">
                <div>
                    <div class="msg-user-bubble">{content}</div>
                    <div class="msg-time">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-giulieta">
                <div class="msg-giulieta-avatar">✦</div>
                <div>
                    <div class="msg-giulieta-bubble">{content}</div>
                    <div class="msg-time">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input de chat
user_input = st.chat_input(f"Fale com a Giulieta, {st.session_state.user_name}...")

if user_input:
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        st.error("Configure sua OpenAI API Key na barra lateral para conversar com a Giulieta.")
    else:
        # Adiciona mensagem do usuário
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": now_str
        })

        # Gera resposta
        with st.spinner(""):
            try:
                reply, emotion = ask_giulieta(
                    st.session_state.user_id,
                    st.session_state.user_name,
                    user_input,
                    api_key
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            except Exception as e:
                st.error(f"Erro ao conectar com a Giulieta: {str(e)}")

        st.rerun()

# Módulos visuais (abaixo do chat)
st.markdown("---")
st.markdown("""
<div style='text-align:center; margin: 1rem 0 0.5rem;'>
    <span style='color:#64748b; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em;'>Módulos da Giulieta</span>
</div>
<div class="module-grid">
    <div class="module-card">
        <div class="module-icon">💬</div>
        <div class="module-name">Chat Inteligente</div>
        <div class="module-status-active">● Ativo</div>
    </div>
    <div class="module-card">
        <div class="module-icon">🧠</div>
        <div class="module-name">Memória Persistente</div>
        <div class="module-status-active">● Ativo</div>
    </div>
    <div class="module-card">
        <div class="module-icon">💚</div>
        <div class="module-name">Inteligência Emocional</div>
        <div class="module-status-active">● Ativo</div>
    </div>
    <div class="module-card">
        <div class="module-icon">📅</div>
        <div class="module-name">Agenda Viva</div>
        <div class="module-status-active">● Ativo</div>
    </div>
    <div class="module-card">
        <div class="module-icon">⏰</div>
        <div class="module-name">Lembretes Humanos</div>
        <div class="module-status-active">● Ativo</div>
    </div>
    <div class="module-card">
        <div class="module-icon">🏥</div>
        <div class="module-name">Saúde & Bem-estar</div>
        <div class="module-status-soon">○ Em breve</div>
    </div>
    <div class="module-card">
        <div class="module-icon">💰</div>
        <div class="module-name">Módulo Financeiro</div>
        <div class="module-status-soon">○ Em breve</div>
    </div>
    <div class="module-card">
        <div class="module-icon">👥</div>
        <div class="module-name">Relacionamentos</div>
        <div class="module-status-soon">○ Em breve</div>
    </div>
    <div class="module-card">
        <div class="module-icon">🏠</div>
        <div class="module-name">Casa & IoT</div>
        <div class="module-status-soon">○ Em breve</div>
    </div>
</div>
""", unsafe_allow_html=True)
