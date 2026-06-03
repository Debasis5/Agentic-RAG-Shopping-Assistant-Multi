import re
import streamlit as st
import streamlit.components.v1 as components
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Aria – ShopEasy",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  html, body, [class*="css"] {
    font-family: "Amazon Ember", Arial, sans-serif;
    background-color: #f3f3f3;
  }

  .block-container {
    padding-top: 10rem !important;
    padding-bottom: 0 !important;
  }


  header[data-testid="stHeader"] { display: none; }
  footer { display: none; }

  /* Keep sidebar visible even when aria-expanded=false */
  section[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
  }
  .eelgd2m0[aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
  }
  /* Hide the collapse button inside the sidebar */
  div[data-testid="stSidebarCollapseButton"] {
    display: none !important;
  }
  /* Hide the reopen arrow (not needed since sidebar never collapses) */
  button[data-testid="collapsedControl"] {
    display: none !important;
  }

  /* Tighten spacing between sidebar elements */
  section[data-testid="stSidebar"] .stElementContainer {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
  }
  section[data-testid="stSidebar"] .stMarkdown {
    margin-bottom: 0 !important;
  }
  section[data-testid="stSidebar"] p {
    margin-top: 0 !important;
    margin-bottom: 0.15rem !important;
  }
  section[data-testid="stSidebar"] ul {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
  }
  section[data-testid="stSidebar"] li {
    margin-bottom: 0.1rem !important;
  }
  section[data-testid="stSidebar"] hr {
    margin: 0.25rem 0 !important;
  }

  /* Sticky top bar — fixed, starts after sidebar */
  .top-sticky {
    position: fixed;
    top: 0;
    left: 310px;
    right: 0;
    z-index: 999;
    background-color: #f3f3f3;
    padding: 6px 1rem 4px 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    overflow: hidden;
  }

  /* Aria header bar */
  .aria-header {
    background: linear-gradient(135deg, #1565c0 0%, #0a2d6e 100%);
    border-radius: 10px;
    padding: 10px 20px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 14px rgba(13, 71, 161, 0.35);
  }
  .aria-header .logo { font-size: 1.5rem; }
  .aria-header h1 {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 2px;
    font-style: italic;
    background: linear-gradient(90deg, #e3f2fd 0%, #90caf9 60%, #ffffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
  }
  .aria-header p {
    margin: 1px 0 0;
    font-size: 0.76rem;
    color: #90caf9;
  }

  /* Suggestion chips */
  .chips-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
  }
  .chip {
    background: #fff;
    border: 1.5px solid #ddd;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #0f1111;
  }

  /* Message bubbles */
  .msg-row { display: flex; margin-bottom: 14px; }
  .msg-row.user      { justify-content: flex-end; }
  .msg-row.assistant { justify-content: flex-start; }

  .bubble {
    max-width: 72%;
    padding: 10px 14px;
    border-radius: 16px;
    font-size: 0.88rem;
    line-height: 1.45;
    word-break: break-word;
  }
  .bubble.user {
    background: #ff9900;
    color: #0f1111;
    border-bottom-right-radius: 4px;
    font-weight: 500;
    white-space: pre-wrap;
  }
  .bubble.assistant {
    max-width: 92%;
    background: #ffffff;
    color: #0f1111;
    border: 1px solid #e3e6e6;
    border-bottom-left-radius: 4px;
  }
  /* Tighten markdown inside assistant bubble */
  .bubble.assistant p  { margin: 0 0 0.3rem 0; }
  .bubble.assistant ul,
  .bubble.assistant ol { margin: 0.2rem 0 0.3rem 0; padding-left: 1.2rem; }
  .bubble.assistant li { margin-bottom: 0.15rem; }
  .bubble.assistant p:last-child,
  .bubble.assistant li:last-child { margin-bottom: 0; }
  .bubble.assistant strong { font-weight: 600; }
  .bubble.assistant h1, .bubble.assistant h2,
  .bubble.assistant h3  { font-size: 0.92rem; margin: 0.3rem 0 0.2rem; }

  /* Avatars */
  .avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0; margin-top: 2px;
  }
  .avatar.aria-av { background: #1a73e8; margin-right: 10px; }
  .avatar.user-av { background: #ff9900; margin-left: 10px; }

  /* Intent badges */
  .badge {
    display: inline-block;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 8px;
    font-weight: 600;
    vertical-align: middle;
  }
  .badge-rag   { background: #e8f4fd; color: #0972d3; }
  .badge-tool  { background: #f0faf4; color: #1a7f37; }
  .badge-chat  { background: #fdf8e8; color: #a04800; }
  .badge-block { background: #fde8e8; color: #c0392b; }

  /* Chat input */
  div[data-testid="stChatInput"] textarea {
    border: 2px solid #ff9900 !important;
    border-radius: 24px !important;
    font-size: 0.95rem !important;
    padding: 12px 18px !important;
    box-shadow: 0 0 8px rgba(255, 153, 0, 0.35), 0 0 2px rgba(255, 153, 0, 0.2) !important;
    transition: box-shadow 0.3s ease !important;
  }
  div[data-testid="stChatInput"] textarea:focus {
    box-shadow: 0 0 14px rgba(255, 153, 0, 0.55), 0 0 4px rgba(255, 153, 0, 0.3) !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="display:flex; align-items:center; gap:12px; padding:4px 4px 6px 4px;">
    <div style="
        width: 52px; height: 52px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 3px 8px rgba(26,115,232,0.4);
        flex-shrink: 0;
    ">🛒</div>
    <div>
        <div style="font-size: 1.35rem; font-weight: 900; letter-spacing: 1px; line-height: 1.1; text-shadow: 0 1px 2px rgba(0,0,0,0.15);">
            <span style="color: #1a73e8;">SHOP</span><span style="color: #0d47a1;">EASY</span>
        </div>
        <div style="color: #888; font-size: 0.68rem; letter-spacing: 1.2px; text-transform: uppercase; margin-top: 2px;">Customer Support</div>
    </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
<p style="font-style:italic; color:#555; font-size:0.85rem; line-height:1.5; border-left:3px solid #1a73e8; padding-left:10px; margin:4px 0;">
Aria is your AI shopping assistant, powered by ShopEasy's knowledge base.
</p>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**What I can do:**")
    st.markdown("- 📦 Track orders & shipments")
    st.markdown("- 🔄 Help with returns & refunds")
    st.markdown("- 💳 Answer payment questions")
    st.markdown("- 📋 Explain store policies")
    st.markdown("- 🙋 General account help")
    # Push clear chat, hotline and caption to the bottom
    st.markdown("""
<div style="position:fixed; bottom:1.2rem; width:220px;">
    <hr style="border-color:#e0e0e0; margin-bottom:0.6rem;">
    <div style="font-size:0.78rem; color:#444; margin-bottom:0.6rem; text-align:center;">📞 <strong>Support hotline</strong><br>
        <span style="font-family:monospace; color:#1a73e8;">1800-3000-9009</span>
    </div>
    <div style="font-size:0.68rem; color:#999; margin-bottom:0.6rem; text-align:center;">Powered by ShopEasy Aria · v1.0</div>
</div>
""", unsafe_allow_html=True)
    # Spacer to push button above the fixed hotline block
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
SUGGESTIONS = [
    "What's your return policy?",
    "Track my order ORD-2024-001",
    "How do I pay with EMI?",
    "What are your shipping charges?",
    "How do I close my account?",
]

chips_html = '<div class="chips-row">' + "".join(
    f'<span class="chip">{s}</span>' for s in SUGGESTIONS
) + "</div>"

st.markdown(f"""
<div class="top-sticky">
  <div class="aria-header">
    <div class="logo">🛍️</div>
    <div>
      <h1>Aria</h1>
      <p>Your ShopEasy AI assistant — ask me anything about your orders, returns, or policies.</p>
    </div>
  </div>
  {chips_html}
  <hr style="margin:4px 0 0 0; border-color:#ddd;">
</div>""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def badge_html(intent: str, guardrail: str) -> str:
    if guardrail == "BLOCK":
        return '<span class="badge badge-block">⛔ blocked</span>'
    mapping = {
        "rag":       ("badge-rag",  "📚 policy"),
        "tool_call": ("badge-tool", "🔧 live data"),
        "chitchat":  ("badge-chat", "💬 chat"),
    }
    cls, label = mapping.get(intent, ("badge-chat", "💬 chat"))
    return f'<span class="badge {cls}">{label}</span>'


def md_to_html(text: str) -> str:
    """Minimal markdown → HTML for chat bubbles."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    lines, out, in_ul = text.split('\n'), [], False
    for line in lines:
        if re.match(r'^[-•]\s+', line):
            if not in_ul:
                out.append('<ul>'); in_ul = True
            out.append(f'<li>{line[2:].strip()}</li>')
        elif re.match(r'^\d+\.\s+', line):
            if not in_ul:
                out.append('<ul>'); in_ul = True
            out.append(f'<li>{re.sub(r"^\d+\.\s+", "", line)}</li>')
        else:
            if in_ul:
                out.append('</ul>'); in_ul = False
            if line.strip():
                out.append(f'<p>{line}</p>')
    if in_ul:
        out.append('</ul>')
    return ''.join(out)


def render_message(role: str, content: str, intent: str = "", guardrail: str = ""):
    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
          <div class="bubble user">{content}</div>
          <div class="avatar user-av">👤</div>
        </div>""", unsafe_allow_html=True)
    else:
        badge = badge_html(intent, guardrail)
        st.markdown(f"""
        <div class="msg-row assistant">
          <div class="avatar aria-av">🛍️</div>
          <div>
            <div style="font-size:0.75rem;color:#6c757d;margin-bottom:4px;">Aria{badge}</div>
            <div class="bubble assistant">{md_to_html(content)}</div>
          </div>
        </div>""", unsafe_allow_html=True)


# ── Chat history ──────────────────────────────────────────────────────────────
WELCOME = "Hi! I'm Aria, your friendly customer support agent at ShopEasy! I'm here to help you with your queries to make your experience smoother."

if not st.session_state.messages:
    render_message("assistant", WELCOME)

for msg in st.session_state.messages:
    render_message(
        msg["role"], msg["content"],
        msg.get("intent", ""), msg.get("guardrail", ""),
    )


# ── Streaming ─────────────────────────────────────────────────────────────────
def stream_response(query: str):
    try:
        with requests.post(
            f"{API_URL}/chat",
            json={"query": query},
            stream=True,
            timeout=60,
        ) as resp:
            resp.raise_for_status()
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data:"):
                    continue
                payload = json.loads(raw[5:].strip())
                if payload["type"] == "token":
                    yield payload["content"], None
                elif payload["type"] == "done":
                    yield "", payload
    except requests.exceptions.ConnectionError:
        yield "⚠️ Cannot reach the API. Make sure `uvicorn api:app` is running on port 8000.", {
            "type": "done", "intent": "", "guardrail_decision": ""
        }


# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask Aria anything about ShopEasy…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    accumulated = ""
    intent_val = ""
    guardrail_val = ""
    placeholder = st.empty()

    # Show animated dots immediately before first token arrives
    placeholder.markdown("""
    <style>
    @keyframes blink {
      0%, 100% { opacity: 0.2; }
      50%       { opacity: 1; }
    }
    .dot { display:inline-block; width:6px; height:6px; border-radius:50%;
           background:#1565c0; margin:0 2px; animation: blink 1.2s infinite; }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    </style>
    <div class="msg-row assistant">
      <div class="avatar aria-av">🛍️</div>
      <div>
        <div style="font-size:0.75rem;color:#6c757d;margin-bottom:4px;">Aria</div>
        <div class="bubble assistant" style="display:inline-flex; align-items:center; padding:10px 16px;">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    for token, meta in stream_response(prompt):
        if meta is not None:
            intent_val = meta.get("intent", "")
            guardrail_val = meta.get("guardrail_decision", "")
        else:
            accumulated += token
            placeholder.markdown(f"""
            <div class="msg-row assistant">
              <div class="avatar aria-av">🛍️</div>
              <div>
                <div style="font-size:0.75rem;color:#6c757d;margin-bottom:4px;">Aria</div>
                <div class="bubble assistant">{accumulated}▌</div>
              </div>
            </div>""", unsafe_allow_html=True)

    badge = badge_html(intent_val, guardrail_val)
    placeholder.markdown(f"""
    <div class="msg-row assistant">
      <div class="avatar aria-av">🛍️</div>
      <div>
        <div style="font-size:0.75rem;color:#6c757d;margin-bottom:4px;">Aria{badge}</div>
        <div class="bubble assistant">{md_to_html(accumulated)}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": accumulated,
        "intent": intent_val,
        "guardrail": guardrail_val,
    })

# Auto-focus + auto-scroll to bottom on every page load/rerun
components.html("""
<script>
  function init() {
    const doc = window.parent.document;

    // Focus chat input
    const el = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
    if (el) { el.focus(); }
    else { setTimeout(init, 150); return; }

    // Scroll main content to bottom
    const main = doc.querySelector('section[data-testid="stMain"] > div:first-child');
    if (main) { main.scrollTop = main.scrollHeight; }
  }
  init();
</script>
""", height=0)
