import streamlit as st
from agents.travel_graph import run_agent

# ── Page Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel Copilot",
    page_icon="✈️",
    layout="centered"
)

# ── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .main { background-color: #f5f7fa; }
        .stChatMessage { border-radius: 15px; }
        .sidebar .sidebar-content { background-color: #1a1a2e; }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/airplane-mode-on.png", width=80)
    st.title("Travel Copilot")
    st.markdown("**Your AI Travel Assistant**")
    st.divider()

    st.markdown("### I can help you with:")
    st.markdown("🛫 Search flights")
    st.markdown("🏨 Find hotels")
    st.markdown("🌤️ Check weather")
    st.markdown("💱 Convert currency")
    st.markdown("🌐 Translate text")
    st.divider()

    st.markdown("### Example queries:")
    st.code("Weather in Hunza")
    st.code("Flights from ISB to DXB")
    st.code("100 USD to PKR")
    st.code("Hotels in Lahore")
    st.code("Translate Hello to Arabic")
    st.divider()

    st.markdown("### Pakistan Tourism 🇵🇰")
    st.markdown("🏔️ Hunza Valley")
    st.markdown("🏔️ Skardu")
    st.markdown("🌿 Naran Kaghan")
    st.markdown("🌲 Murree")
    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main Header ────────────────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align: center; color: #1a73e8;'>
        ✈️ Travel Copilot
    </h1>
    <p style='text-align: center; color: gray;'>
        Your AI-powered travel assistant
    </p>
""", unsafe_allow_html=True)

st.divider()

# ── Chat History ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Welcome Message ────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hello! I'm **Travel Copilot**, your AI travel assistant!\n\n"
            "I can help you with:\n"
            "- ✈️ **Flights** — Search available flights\n"
            "- 🏨 **Hotels** — Find hotels in any city\n"
            "- 🌤️ **Weather** — Check weather anywhere\n"
            "- 💱 **Currency** — Convert between currencies\n"
            "- 🌐 **Translation** — Translate text instantly\n\n"
            "What are you planning today? 🗺️"
        )

# ── Display Chat History ───────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ─────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about travel..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Searching...✈️"):
            response = run_agent(
                prompt,
                st.session_state.messages[:-1]
            )
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})