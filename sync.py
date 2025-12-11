import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load Environment Variables (.env)
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Verifica se a chave existe
if not api_key:
    st.error("ERRO: A chave API do Groq não foi encontrada. Verifique seu arquivo .env")
    st.stop()

# 2. Inicializa o Cliente Groq
client = Groq(api_key=api_key)

# 3. Page Configuration
st.set_page_config(
    page_title="SYNC",
    page_icon="💘",
    layout="centered"
)

# --- A. DEFINIÇÃO DOS PERFIS & PERSONALIDADES (SYSTEM PROMPTS) ---
# Dica: O "system_prompt" é onde a mágica acontece.
profiles = [
    {
        "name": "Belle", 
        "age": 21,
        "hobbies": "Music, Gym, Kart",
        "artists": "Lagum, Leo Foguete, João Gomes",
        "watching": "Gilmore Girls (Season 7)",
        "mood": "☕ Up for a coffee and deep conversation.",
        "system_prompt": """
            Você é Belle, uma jovem de 21 anos.
            Personalidade: Calma, introspectiva, adora uma vibe "clean girl aesthetic", mas também adora velocidade (kart).
            Gostos Musicais: Lagum e piseiro brasileiro.
            Tom de voz: Amigável, usa emojis fofos (☕, ✨), fala de forma casual e carinhosa.
            Objetivo: Quer encontrar alguém para conversas profundas em um café.
            Regra: Pode usar gírias leves da internet. Mantenha respostas curtas (máximo 2 frases).
        """
    },
    {
        "name": "Odete Roitman", 
        "age": 65,
        "hobbies": "Make money, Lie, Drive",
        "artists": "Valesca Popozuda, Fifth Harmony, Dopamoon",
        "watching": "Dynasty (Season 2)",
        "mood": "💵 Looking for someone I could invest some dollars in.",
        "system_prompt": """
            Você é a icônica vilã Odete Roitman.
            Personalidade: Arrogante, elitista, ácida, odeia a pobreza e o clima tropical do Brasil. Ama Paris.
            Tom de voz: Sarcástico, direto, impaciente. Usa palavras como "cafona", "pobreza", "elegância".
            Objetivo: Julgar o usuário e ver se ele é digno do seu tempo (e dinheiro).
            Regra: Se o usuário for simpático demais, desconfie. Mantenha respostas curtas e afiadas.
        """
    },
    {
        "name": "Liz Felpa", 
        "age": 20,
        "hobbies": "Python, Kart, Guitar",
        "artists": "Arctic Monkeys, Post Malone, Joji",
        "watching": "Dexter (Season 4)",
        "mood": "🎮 Looking for someone to play FIFA with.",
        "system_prompt": """
            Você é Liz Felpa, uma programadora e gamer de 20 anos.
            Personalidade: Geek, engraçada, meio nerd, adora código e música indie.
            Tom de voz: Descolado, usa gírias de dev (bug, deploy, feature), refere-se a coisas como se fossem jogos ou código.
            Objetivo: Achar um "player 2" para jogar FIFA ou codar junto.
            Regra: Mantenha respostas curtas e divertidas.
        """
    }
]

# --- B. GERENCIAMENTO DE ESTADO ---

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'discovery'

if 'active_match' not in st.session_state:
    st.session_state.active_match = None

if 'profile_index' not in st.session_state:
    st.session_state.profile_index = 0

if 'matches' not in st.session_state:
    st.session_state.matches = []

# Histórico: {'Nome': [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]}
if 'chat_histories' not in st.session_state:
    st.session_state.chat_histories = {}

# --- C. FUNÇÕES AUXILIARES ---

def get_groq_response(messages, system_prompt):
    """
    Função atualizada para o modelo Llama 3.3 (Versatile)
    """
    try:
        # Cria uma lista temporária para a API contendo a instrução do sistema + histórico
        api_messages = [{"role": "system", "content": system_prompt}] + messages
        
        chat_completion = client.chat.completions.create(
            messages=api_messages,
            # ATUALIZADO: Usando o modelo mais recente e estável do Groq
            model="llama-3.3-70b-versatile", 
            temperature=0.8, # Um pouco mais criativo para as piadas
            max_completion_tokens=200,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na conexão com Groq: {e}"

def next_profile():
    st.session_state.profile_index += 1

def sync_person():
    person = profiles[st.session_state.profile_index]
    st.session_state.matches.append(person)
    if person['name'] not in st.session_state.chat_histories:
        st.session_state.chat_histories[person['name']] = []
    st.session_state.profile_index += 1

def open_chat(person):
    st.session_state.active_match = person
    st.session_state.current_view = 'chat'

def back_to_discovery():
    st.session_state.active_match = None
    st.session_state.current_view = 'discovery'

# --- D. ESTILOS CSS ---
st.markdown("""
    <style>
    .main-title { font-size: 80px !important; font-weight: 700; color: #FF4B4B; text-align: center; margin-bottom: 0px; line-height: 1; }
    .sidebar-title { font-size: 50px !important; font-weight: 700; color: #FF4B4B; text-align: center; margin-bottom: 20px; line-height: 1; }
    .slogan { font-size: 24px; font-style: italic; color: #666; text-align: center; margin-top: 10px; margin-bottom: 20px; }
    .category-label { font-weight: bold; color: #FF4B4B; margin-bottom: 5px; margin-top: 0px; }
    .end-message { text-align: center; font-size: 20px; color: #666; margin-top: 50px; }
    .chat-header-name { font-size: 32px; font-weight: bold; margin-bottom: 0px; }
    .chat-header-mood { font-size: 16px; color: #666; font-style: italic; margin-top: -5px; margin-bottom: 20px; }
    
    .footer {
        position: fixed;
        bottom: 10px;
        right: 15px;
        width: auto;
        background-color: transparent;
        color: #e0e0e0;
        text-align: right;
        font-size: 14px;
        font-weight: bold;
        padding: 5px;
        z-index: 1000;
        opacity: 0.8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">Developed by: Felipe Guimarães</div>', unsafe_allow_html=True)

# --- E. SIDEBAR ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">SYNC</p>', unsafe_allow_html=True)
    st.header(f"Your Syncs ({len(st.session_state.matches)})")
    
    if not st.session_state.matches:
        st.write("People you synced with appear here.")
        st.divider()
        st.caption("No sync yet. Start syncing!")
    else:
        st.divider()
        for match in st.session_state.matches:
            with st.expander(f"💘 {match['name']}, {match['age']}"):
                st.caption("Daily Sync Mood:")
                st.write(match['mood'])
                st.button("Send Message 💬", key=f"msg_{match['name']}", on_click=open_chat, args=(match,))

# --- F. LÓGICA PRINCIPAL ---

# TELA 1: DISCOVERY
if st.session_state.current_view == 'discovery':
    st.markdown('<p class="main-title">SYNC</p>', unsafe_allow_html=True)
    st.markdown('<p class="slogan">Don\'t just match. Sync.</p>', unsafe_allow_html=True)
    st.divider()

    if st.session_state.profile_index < len(profiles):
        current_profile = profiles[st.session_state.profile_index]
        st.markdown(f"## {current_profile['name']}, {current_profile['age']}")

        with st.container(border=True):
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                st.markdown('<p class="category-label">Hobbies 🎨</p>', unsafe_allow_html=True)
                st.info(current_profile['hobbies'])
            with c2:
                st.markdown('<p class="category-label">Currently Watching 📺</p>', unsafe_allow_html=True)
                st.info(current_profile['watching'])
            
            c3, c4 = st.columns(2, gap="medium")
            with c3:
                st.markdown('<p class="category-label">Favorite Artists 🎵</p>', unsafe_allow_html=True)
                st.info(current_profile['artists'])
            with c4:
                st.markdown('<p class="category-label">Daily Sync Mood ⚡</p>', unsafe_allow_html=True)
                st.warning(current_profile['mood'])

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("❌ Pass", use_container_width=True, on_click=next_profile)
        with col_btn2:
            st.button("💘 SYNC", type="primary", use_container_width=True, on_click=sync_person)
    else:
        st.markdown('<p class="end-message">💖 That\'s everyone for now! Check back later.</p>', unsafe_allow_html=True)

# TELA 2: CHAT COM GROQ
elif st.session_state.current_view == 'chat':
    active_person = st.session_state.active_match
    
    if st.button("⬅️ Back to Discovery"):
        back_to_discovery()
        st.rerun()
    
    st.markdown(f'<p class="chat-header-name">{active_person["name"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="chat-header-mood">Daily Sync Mood: {active_person["mood"]}</p>', unsafe_allow_html=True)
    st.divider()

    history = st.session_state.chat_histories[active_person['name']]

    if not history:
        with st.chat_message("assistant"):
            intro_msg = f"You synced with {active_person['name']}! Say hello."
            st.write(intro_msg)

    # Renderiza mensagens antigas
    for message in history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input do usuário
    if prompt := st.chat_input(f"Message {active_person['name']}..."):
        
        # 1. Adiciona e exibe mensagem do usuário
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # 2. Chama a API do Groq
        with st.chat_message("assistant"):
            with st.spinner(f"{active_person['name']} is typing..."):
                
                # Chamada real à API
                response_text = get_groq_response(
                    messages=history, 
                    system_prompt=active_person['system_prompt']
                )
                
                st.write(response_text)
        
        # 3. Salva resposta no histórico
        history.append({"role": "assistant", "content": response_text})