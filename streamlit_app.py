import os
import re
import streamlit as st
import streamlit.components.v1 as components
import requests
import json

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Aria – ShopEasy",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');

  html, body, [class*="css"] {
    font-family: "Inter", "Amazon Ember", Arial, sans-serif;
    background-color: #f3f3f3;
  }

  .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
  }

  section[data-testid="stMain"] > div:first-child {
    padding-top: 0 !important;
  }

  header[data-testid="stHeader"] { display: none; }
  footer { display: none; }

  /* Sidebar — Streamlit keeps it fixed natively; just pin visibility */
  section[data-testid="stSidebar"] {
    transform: translateX(0) !important;
    margin-left: 0 !important;
    min-width: 244px !important;
    visibility: visible !important;
  }
  section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: translateX(0) !important;
    margin-left: 0 !important;
  }
  div[data-testid="stSidebarCollapseButton"],
  button[data-testid="collapsedControl"] { display: none !important; }

  /* Tighten sidebar spacing */
  section[data-testid="stSidebar"] .stElementContainer { margin-bottom: 0 !important; padding-bottom: 0 !important; }
  section[data-testid="stSidebar"] .stMarkdown         { margin-bottom: 0 !important; }
  section[data-testid="stSidebar"] p  { margin-top: 0 !important; margin-bottom: 0.15rem !important; }
  section[data-testid="stSidebar"] ul { margin-top: 0 !important; margin-bottom: 0 !important; padding-top: 0 !important; }
  section[data-testid="stSidebar"] li { margin-bottom: 0.1rem !important; }
  section[data-testid="stSidebar"] hr { margin: 0.25rem 0 !important; }

  /* Suggestion chips (used inside fixed header bar) */
  .chips-row { display: flex; flex-wrap: nowrap; gap: 8px; overflow-x: auto; }
  .chip {
    background: #fff;
    border: 1.5px solid #ddd;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.72rem;
    color: #0f1111;
    white-space: nowrap;
    flex-shrink: 0;
  }

  /* Message bubbles */
  .msg-row { display: block; margin-bottom: 14px; }
  .msg-row.user .msg-inner {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    margin-left: auto;
    max-width: 80%;
  }
  .msg-row.assistant .msg-inner {
    display: flex;
    align-items: flex-start;
    max-width: 92%;
  }
  .bubble {
    padding: 11px 15px;
    border-radius: 18px;
    font-size: 0.82rem;
    line-height: 1.65;
    word-break: break-word;
    letter-spacing: 0.01em;
  }
  .bubble.user {
    background: #ff9900;
    color: #0f1111;
    border-bottom-right-radius: 4px;
    font-family: "DM Sans", "Inter", Arial, sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    white-space: pre-wrap;
    max-width: 100%;
    letter-spacing: 0.01em;
  }
  .bubble.assistant {
    background: #ffffff;
    color: #1a1a2e;
    border: 1px solid #e3e6e6;
    border-bottom-left-radius: 4px;
    max-width: 100%;
    font-family: "DM Sans", "Inter", Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 400;
    line-height: 1.7;
  }
  @media (prefers-color-scheme: dark) {
    .bubble.assistant { background: #2a2d35 !important; color: #e8eaed !important; border-color: #3c4049 !important; }
    .chip { background: #1e2128 !important; border-color: #3c4049 !important; color: #e8eaed !important; }
  }
  .bubble.assistant p  { margin: 0 0 0.3rem 0; font-size: 0.82rem; line-height: 1.7; }
  .bubble.assistant ul,
  .bubble.assistant ol { margin: 0.2rem 0 0.3rem 0; padding-left: 1.3rem; }
  .bubble.assistant li { margin-bottom: 0.18rem; font-size: 0.82rem; line-height: 1.6; }
  .bubble.assistant p:last-child,
  .bubble.assistant li:last-child { margin-bottom: 0; }
  .bubble.assistant strong { font-weight: 600; color: inherit; }
  .bubble.assistant h1, .bubble.assistant h2,
  .bubble.assistant h3  { font-size: 0.85rem; font-weight: 700; margin: 0.3rem 0 0.18rem; letter-spacing: 0.02em; }

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
    display: inline-block; font-size: 0.7rem; padding: 2px 8px;
    border-radius: 10px; margin-left: 8px; font-weight: 600; vertical-align: middle;
  }
  .badge-rag        { background: #e8f4fd; color: #0972d3; }
  .badge-tool       { background: #f0faf4; color: #1a7f37; }
  .badge-escalation { background: #fdf0f8; color: #8e24aa; }
  .badge-chat       { background: #fdf8e8; color: #a04800; }
  .badge-block      { background: #fde8e8; color: #c0392b; }

  /* Chat input */
  div[data-testid="stChatInput"] textarea {
    border: 2px solid #ff9900 !important;
    border-radius: 24px !important;
    font-size: 0.95rem !important;
    padding: 12px 18px !important;
    box-shadow: 0 0 8px rgba(255,153,0,0.35) !important;
    transition: box-shadow 0.3s ease !important;
  }
  div[data-testid="stChatInput"] textarea:focus {
    box-shadow: 0 0 14px rgba(255,153,0,0.55) !important;
    outline: none !important;
  }
  div[data-testid="stChatInput"] > div {
    outline: none !important; box-shadow: none !important;
    border: none !important; display: flex !important; align-items: center !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False


# ── Agent-flow diagram HTML template ─────────────────────────────────────────
FLOW_DIAGRAM_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {{
  --af-bg:       #eef0f4; --af-border: #b8beca; --af-card-bg: #ffffff;
  --af-card-bd:  #9aa2b4; --af-sup-bg: #e4e8f0; --af-sup-bd:  #8892a8;
  --af-idle-lbl: #2c3142; --af-idle-sub: #4a5268; --af-idle-con: #8892a8;
  --af-meta:     #3d4458; --af-head-txt: #111520; --af-shadow: rgba(0,0,0,0.12);
  --af-active-con: #e07000; --af-active-gap: #eef0f4;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --af-bg:       #0e1117; --af-border: #2a2d35; --af-card-bg: #1e2130;
    --af-card-bd:  #353848; --af-sup-bg: #262a3a; --af-sup-bd:  #404560;
    --af-idle-lbl: #a8b0c8; --af-idle-sub: #7a82a0; --af-idle-con: #404560;
    --af-meta:     #8890a8; --af-head-txt: #e8ecf8; --af-shadow: rgba(0,0,0,0.35);
    --af-active-con: #4d9fff; --af-active-gap: #0e1117;
  }}
}}
* {{ box-sizing: border-box; font-family: "Inter", "Amazon Ember", Arial, sans-serif; }}
body {{ margin:0; background: var(--af-bg); }}
.af-panel {{
  position: fixed; top: 0; right: 0; height: 100vh;
  background: var(--af-bg); border-left: 1px solid var(--af-border);
  box-shadow: -2px 0 10px var(--af-shadow);
  display: flex; flex-direction: column; overflow-y: auto; overflow-x: hidden;
}}
.af-header {{
  display: flex; align-items: center; gap: 12px;
  padding: 4px 14px 6px 14px; flex-shrink: 0;
  border-bottom: 1px solid var(--af-border);
}}
.af-header-icon {{
  width: 52px; height: 52px; min-width: 52px; border-radius: 50%;
  background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; box-shadow: 0 3px 8px rgba(26,115,232,0.4); flex-shrink: 0;
}}
.af-header-text {{ display: flex; flex-direction: column; justify-content: center; }}
.af-header-title {{
  font-size: 1.2rem; font-weight: 900; letter-spacing: 1px; line-height: 1.1; margin: 0;
  white-space: nowrap;
}}
.af-header-title .t1 {{ color: #1a73e8; }}
.af-header-title .t2 {{ color: #0d47a1; }}
.af-header-sub {{
  font-size: 0.68rem; letter-spacing: 1.2px; text-transform: uppercase;
  color: var(--af-meta); margin-top: 2px; line-height: 1;
}}
.af-status {{
  padding: 8px 16px 0 16px; font-size: 0.6rem; color: var(--af-meta);
  letter-spacing: 0.5px; text-transform: uppercase; flex-shrink: 0;
}}
.af-status-dot {{
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: #e07000; margin-right: 5px; vertical-align: middle;
  transition: background 0.4s;
}}
@media (prefers-color-scheme: dark) {{
  .af-status-dot {{ background: var(--af-meta); }}
}}
.af-status-dot.live {{ background: #34a853; animation: af-pulse-dot 1.5s infinite; }}
.af-status-dot.executing {{ background: #ff9900; animation: af-pulse-dot 0.8s infinite; }}
@keyframes af-pulse-dot {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.35; }} }}
.af-divider {{ margin: 8px 16px 0 16px; height: 1px; background: var(--af-border); flex-shrink: 0; }}
.af-tree {{
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 10px 14px 16px 14px;
}}

/* Query box */
.af-query-box {{
  width: 100%; border: 1.5px solid var(--af-card-bd); border-radius: 8px;
  padding: 7px 10px; background: var(--af-card-bg); box-shadow: 0 1px 3px var(--af-shadow); text-align: center;
}}
.af-query-label {{ display: block; font-size: 0.54rem; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: var(--af-meta); margin-bottom: 3px; }}
.af-query-text  {{ display: block; font-size: 0.6rem; color: var(--af-head-txt); line-height: 1.35; word-break: break-word; max-height: 2.8em; overflow: hidden; font-style: italic; opacity: 0.85; }}
.af-query-box.has-query {{ border-color: #ff9900; box-shadow: 0 0 6px rgba(255,153,0,0.25); }}
.af-query-box.has-query .af-query-label {{ color: #ff9900; }}
.af-query-box.has-query .af-query-text  {{ opacity: 1; font-style: normal; }}

/* Supervisor box */
.af-supervisor-box {{
  width: 100%; border: 1.5px solid var(--af-sup-bd); border-radius: 10px;
  padding: 8px 10px 10px 10px; background: var(--af-sup-bg); box-shadow: 0 1px 4px var(--af-shadow);
}}
.af-supervisor-label {{ font-size: 0.67rem; font-weight: 800; color: var(--af-head-txt); letter-spacing: 0.4px; text-align: center; }}
.af-supervisor-sub   {{ font-size: 0.54rem; color: var(--af-meta); text-align: center; margin-top: 1px; margin-bottom: 7px; }}
.af-sup-nodes {{ display: flex; gap: 7px; }}
.af-sup-node {{
  flex: 1; border: 1.5px solid var(--af-card-bd); border-radius: 7px;
  padding: 6px 4px 5px 4px; background: var(--af-card-bg); text-align: center;
  transition: background 0.45s, border-color 0.45s, box-shadow 0.45s;
}}
.af-sup-node .af-label {{ display: block; font-weight: 700; font-size: 0.65rem; color: var(--af-idle-lbl); }}
.af-sup-node .af-sub   {{ display: block; font-size: 0.52rem; color: var(--af-idle-sub); margin-top: 1px; }}

/* Animated connectors */
.af-v-line {{ width: 2px; height: 20px; background: var(--af-idle-con); transition: background 0.4s; position: relative; z-index: 2; }}
.af-v-line.active {{
  background: repeating-linear-gradient(to bottom, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 2px 8px;
  animation: af-flow-down 0.5s linear infinite;
}}
@keyframes af-flow-down {{ from {{ background-position: 0 0; }} to {{ background-position: 0 8px; }} }}

/* Per-agent column layout */
.af-agent-grid {{
  display: flex; gap: 5px; width: 100%;
}}
.af-agent-col {{
  flex: 1; display: flex; flex-direction: column; align-items: center;
}}

/* Horizontal bus row — one cell per agent column */
.af-h-bus {{
  display: flex; width: 100%; height: 10px; gap: 5px;
  position: relative; z-index: 2;
}}
.af-h-seg {{
  flex: 1; height: 100%; display: flex; align-items: center;
}}
.af-h-seg-line {{
  width: 100%; height: 2px; background: var(--af-idle-con); transition: background 0.4s;
}}
/* Active full-width segments (bridge): animate the whole line */
.af-h-seg.active .af-h-seg-line {{
  background: repeating-linear-gradient(to right, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 8px 2px;
  animation: af-flow-right 0.5s linear infinite;
}}
@keyframes af-flow-right {{ from {{ background-position: 0 0; }} to {{ background-position: 8px 0; }} }}

/* Clipped active segments: show gray full-width line, then overlay animated half via ::after */
/* seg-outer-left (chitchat col): active half is right 50% */
.af-h-seg.seg-outer-left.active .af-h-seg-line {{
  background: var(--af-idle-con); position: relative;
}}
.af-h-seg.seg-outer-left.active .af-h-seg-line::after {{
  content: ''; position: absolute; top: 0; bottom: 0; right: 0; width: 50%;
  background: repeating-linear-gradient(to right, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 8px 2px;
  animation: af-flow-right 0.5s linear infinite;
}}
/* seg-inner-left (rag col): active half is right 50% */
.af-h-seg.seg-inner-left.active .af-h-seg-line {{
  background: var(--af-idle-con); position: relative;
}}
.af-h-seg.seg-inner-left.active .af-h-seg-line::after {{
  content: ''; position: absolute; top: 0; bottom: 0; right: 0; width: 50%;
  background: repeating-linear-gradient(to right, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 8px 2px;
  animation: af-flow-right 0.5s linear infinite;
}}
/* seg-inner-right (order col): active half is left 50% */
.af-h-seg.seg-inner-right.active .af-h-seg-line {{
  background: var(--af-idle-con); position: relative;
}}
.af-h-seg.seg-inner-right.active .af-h-seg-line::after {{
  content: ''; position: absolute; top: 0; bottom: 0; left: 0; width: 50%;
  background: repeating-linear-gradient(to right, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 8px 2px;
  animation: af-flow-right 0.5s linear infinite;
}}
/* seg-outer-right (escalation col): active half is left 50% */
.af-h-seg.seg-outer-right.active .af-h-seg-line {{
  background: var(--af-idle-con); position: relative;
}}
.af-h-seg.seg-outer-right.active .af-h-seg-line::after {{
  content: ''; position: absolute; top: 0; bottom: 0; left: 0; width: 50%;
  background: repeating-linear-gradient(to right, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 8px 2px;
  animation: af-flow-right 0.5s linear infinite;
}}

.af-drop {{
  width: 2px; display: flex; flex-direction: column;
  position: relative; z-index: 2;
}}
/* Active top drop: .af-drop-gray stays grey always; .af-drop-live animates when active */
.af-drop.drop-top.active .af-drop-gray {{
  background: var(--af-idle-con);
}}
.af-drop.drop-top.active .af-drop-live {{
  background: repeating-linear-gradient(to bottom, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 2px 8px;
  animation: af-flow-down 0.5s linear infinite;
}}
/* Active bottom drop: .af-drop-live animates; .af-drop-gray stays grey */
.af-drop.drop-bot.active .af-drop-live {{
  background: repeating-linear-gradient(to bottom, var(--af-active-con) 0px, var(--af-active-con) 4px, var(--af-active-gap) 4px, var(--af-active-gap) 8px);
  background-size: 2px 8px;
  animation: af-flow-down 0.5s linear infinite;
}}
.af-drop.drop-bot.active .af-drop-gray {{
  background: var(--af-idle-con);
}}
/* Inner half-segments */
.af-drop-gray, .af-drop-live {{
  width: 2px; height: 7px; background: var(--af-idle-con);
}}

/* Agent nodes */
.af-row-agents {{ display: flex; gap: 5px; width: 100%; }}
.af-agent {{
  flex: 1; border: 1.5px solid var(--af-card-bd); border-radius: 8px;
  padding: 7px 3px 6px 3px; background: var(--af-card-bg); text-align: center;
  box-shadow: 0 1px 3px var(--af-shadow);
  transition: background 0.45s, border-color 0.45s, box-shadow 0.45s;
  position: relative; z-index: 1;
}}
.af-agent .af-label {{ display: block; font-weight: 700; font-size: 0.6rem; color: var(--af-idle-lbl); line-height: 1.3; }}
.af-agent .af-sub   {{ display: block; font-size: 0.48rem; color: var(--af-idle-sub); margin-top: 2px; line-height: 1.3; }}

/* Synthesis */
.af-row-synthesis {{ display: flex; flex-direction: column; align-items: center; width: 100%; }}
.af-synthesis {{
  width: 100%; border: 1.5px solid var(--af-card-bd); border-radius: 8px;
  padding: 7px 8px; background: var(--af-card-bg); text-align: center;
  box-shadow: 0 1px 3px var(--af-shadow);
  transition: background 0.45s, border-color 0.45s, box-shadow 0.45s;
}}
.af-synthesis .af-label {{ display: block; font-weight: 700; font-size: 0.65rem; color: var(--af-idle-lbl); }}
.af-synthesis .af-sub   {{ display: block; font-size: 0.52rem; color: var(--af-idle-sub); margin-top: 1px; }}

/* Active: blue */
.af-sup-node.active, .af-agent.active, .af-synthesis.active {{
  border-color: var(--af-active-con) !important; background: #1a3a6e !important;
  animation: af-glow-blue 0.7s ease-out forwards;
}}
.af-sup-node.active .af-label, .af-agent.active .af-label, .af-synthesis.active .af-label {{ color: #7eb8f7 !important; }}
.af-sup-node.active .af-sub,   .af-agent.active .af-sub,   .af-synthesis.active .af-sub   {{ color: #5a90d0 !important; }}
@media (prefers-color-scheme: light) {{
  .af-sup-node.active, .af-agent.active, .af-synthesis.active {{ background: #e8f0fe !important; }}
  .af-sup-node.active .af-label, .af-agent.active .af-label, .af-synthesis.active .af-label {{ color: #1565c0 !important; }}
  .af-sup-node.active .af-sub,   .af-agent.active .af-sub,   .af-synthesis.active .af-sub   {{ color: #5a9cf0 !important; }}
}}

/* Final: orange */
.af-agent.final, .af-synthesis.final {{
  border-color: #ff9900 !important; background: #4a2e00 !important;
  animation: af-glow-orange 0.7s ease-out forwards !important;
}}
.af-agent.final .af-label, .af-synthesis.final .af-label {{ color: #ffb74d !important; }}
.af-agent.final .af-sub,   .af-synthesis.final .af-sub   {{ color: #e8922a !important; }}
@media (prefers-color-scheme: light) {{
  .af-agent.final, .af-synthesis.final {{ background: #fff3e0 !important; }}
  .af-agent.final .af-label, .af-synthesis.final .af-label {{ color: #bf5e00 !important; }}
  .af-agent.final .af-sub,   .af-synthesis.final .af-sub   {{ color: #e8922a !important; }}
}}

/* Blocked: red */
.af-sup-node.blocked {{ border-color: #c0392b !important; background: #3a0a08 !important; animation: af-glow-red 0.7s ease-out forwards !important; }}
.af-sup-node.blocked .af-label {{ color: #e57373 !important; }}
@media (prefers-color-scheme: light) {{
  .af-sup-node.blocked {{ background: #fde8e8 !important; }}
  .af-sup-node.blocked .af-label {{ color: #a93226 !important; }}
}}
.af-block-badge {{ display: none; font-size: 0.5rem; font-weight: 700; background: #c0392b; color: #fff; border-radius: 3px; padding: 1px 4px; margin-top: 2px; }}
.af-block-badge.show {{ display: inline-block; }}

@keyframes af-glow-blue   {{ 0% {{ box-shadow:0 0 0 rgba(26,115,232,0); }} 50% {{ box-shadow:0 0 10px rgba(26,115,232,0.55); }} 100% {{ box-shadow:0 0 5px rgba(26,115,232,0.2); }} }}
@keyframes af-glow-orange {{ 0% {{ box-shadow:0 0 0 rgba(255,153,0,0); }} 50% {{ box-shadow:0 0 10px rgba(255,153,0,0.6); }} 100% {{ box-shadow:0 0 5px rgba(255,153,0,0.25); }} }}
@keyframes af-glow-red    {{ 0% {{ box-shadow:0 0 0 rgba(192,57,43,0); }} 50% {{ box-shadow:0 0 10px rgba(192,57,43,0.55); }} 100% {{ box-shadow:0 0 5px rgba(192,57,43,0.2); }} }}
</style>

<div class="af-panel" id="af-panel-inner">
  <div class="af-header">
    <div class="af-header-icon">&#x26A1;</div>
    <div class="af-header-text">
      <div class="af-header-title"><span class="t1">AGENT</span><span class="t2"> FLOW</span></div>
      <div class="af-header-sub">Live Execution Trace</div>
    </div>
  </div>
  <div class="af-status">
    <span class="af-status-dot {cls_dot_live}"></span>{status_label}
  </div>
  <div class="af-divider"></div>
  <div class="af-tree">
    <div class="af-query-box {cls_query_box}">
      <span class="af-query-label">&#x1F4AC; User Query</span>
      <span class="af-query-text">{query_text}</span>
    </div>
    <div class="af-v-line {cls_query_arrow}"></div>
    <div class="af-supervisor-box">
      <div class="af-supervisor-label">Supervisor Agent</div>
      <div class="af-supervisor-sub">Own graph &middot; orchestrates sub-agents</div>
      <div class="af-sup-nodes">
        <div class="af-sup-node {cls_guardrail}">
          <span class="af-label">&#x1F6E1; Guardrail</span>
          <span class="af-sub">Safety + scope</span>
          <span class="af-block-badge {cls_block_label}">BLOCK</span>
        </div>
        <div class="af-sup-node {cls_router}">
          <span class="af-label">&#x1F500; Router</span>
          <span class="af-sub">Which agent?</span>
        </div>
      </div>
    </div>
    <div class="af-v-line {cls_arrow_gr_dr}"></div>
    <div class="af-h-bus">
      <div class="af-h-seg {clip_hseg_0} {cls_hseg_0}"><div class="af-h-seg-line"></div></div>
      <div class="af-h-seg {clip_hseg_1} {cls_hseg_1}"><div class="af-h-seg-line"></div></div>
      <div class="af-h-seg {clip_hseg_2} {cls_hseg_2}"><div class="af-h-seg-line"></div></div>
      <div class="af-h-seg {clip_hseg_3} {cls_hseg_3}"><div class="af-h-seg-line"></div></div>
    </div>
    <div class="af-agent-grid">
      <div class="af-agent-col">
        <div class="af-drop drop-top {cls_tick_chitchat}"><div class="af-drop-gray"></div><div class="af-drop-live"></div></div>
        <div class="af-agent {cls_chitchat}"><span class="af-label">&#x1F4AC; Chitchat</span><span class="af-sub">inline</span></div>
        <div class="af-drop drop-bot {cls_tick_chitchat}"><div class="af-drop-live"></div><div class="af-drop-gray"></div></div>
      </div>
      <div class="af-agent-col">
        <div class="af-drop drop-top {cls_tick_rag}"><div class="af-drop-gray"></div><div class="af-drop-live"></div></div>
        <div class="af-agent {cls_rag}"><span class="af-label">&#x1F4DA; RAG</span><span class="af-sub">rag &#x2192; resp</span></div>
        <div class="af-drop drop-bot {cls_tick_rag}"><div class="af-drop-live"></div><div class="af-drop-gray"></div></div>
      </div>
      <div class="af-agent-col">
        <div class="af-drop drop-top {cls_tick_order}"><div class="af-drop-gray"></div><div class="af-drop-live"></div></div>
        <div class="af-agent {cls_order}"><span class="af-label">&#x1F4E6; Order</span><span class="af-sub">tool &#x2192; resp</span></div>
        <div class="af-drop drop-bot {cls_tick_order}"><div class="af-drop-live"></div><div class="af-drop-gray"></div></div>
      </div>
      <div class="af-agent-col">
        <div class="af-drop drop-top {cls_tick_escalation}"><div class="af-drop-gray"></div><div class="af-drop-live"></div></div>
        <div class="af-agent {cls_escalation}"><span class="af-label">&#x1F6A8; Escalation</span><span class="af-sub">complaint &#x2192; ticket</span></div>
        <div class="af-drop drop-bot {cls_tick_escalation}"><div class="af-drop-live"></div><div class="af-drop-gray"></div></div>
      </div>
    </div>
    <div class="af-h-bus">
      <div class="af-h-seg {clip_hseg_0} {cls_hseg_0}"><div class="af-h-seg-line"></div></div>
      <div class="af-h-seg {clip_hseg_1} {cls_hseg_1}"><div class="af-h-seg-line"></div></div>
      <div class="af-h-seg {clip_hseg_2} {cls_hseg_2}"><div class="af-h-seg-line"></div></div>
      <div class="af-h-seg {clip_hseg_3} {cls_hseg_3}"><div class="af-h-seg-line"></div></div>
    </div>
    <div class="af-v-line {cls_arrow_agents_syn}"></div>
    <div class="af-row-synthesis">
      <div class="af-synthesis {cls_synthesis}">
        <span class="af-label">&#x26A1; Synthesis</span>
        <span class="af-sub">Merge + faithfulness check</span>
      </div>
    </div>
  </div>
</div>
"""


def _get_flow_state() -> tuple[set, str, bool]:
    if st.session_state.get("processing", False):
        return set(), "", True
    msgs = st.session_state.get("messages", [])
    last = next((m for m in reversed(msgs) if m["role"] == "assistant"), None)
    if last is None:
        return set(), "", False
    guardrail = last.get("guardrail", "")
    outcome   = last.get("agent_outcome", "")
    if guardrail == "BLOCK":
        return {"guardrail"}, "guardrail", False
    active = {"guardrail", "delegation_router", outcome, "synthesis"}
    return active, outcome, False


def _build_flow_classes(active: set, final: str, is_processing: bool = False) -> dict:
    is_block = (final == "guardrail")

    def node_cls(node_id):
        if node_id == "guardrail" and is_block: return "blocked"
        if node_id == final: return "active final"
        if node_id in active: return "active"
        return ""

    def arrow_cls(*required):
        return "active" if all(n in active for n in required) else ""

    def tick_cls(agent_id):
        return "active" if agent_id in active else ""

    # Horizontal bus: 4 segments, one per agent column.
    # Router v-line drops between seg_1 (RAG) and seg_2 (Order).
    # Each segment also carries a half-clip class:
    #   seg_0 (chitchat)   → outer-left  (only right half draws, no dangle left)
    #   seg_1 (rag)        → inner-right (only right half draws — from center drop down to RAG)
    #   seg_2 (order)      → inner-left  (only left half draws — from center drop down to Order)
    #   seg_3 (escalation) → outer-right (only left half draws, no dangle right)
    # Active segments per agent:
    #   chitchat   → segs 0+1  (line goes left: center→RAG col→Chitchat col)
    #   rag        → seg 1     (right half of seg_1 only, drops straight from center)
    #   order      → seg 2     (left half of seg_2 only, drops straight from center)
    #   escalation → segs 2+3  (line goes right: center→Order col→Escalation col)
    seg_active_map = {
        "chitchat":   {0, 1},
        "rag":        {1},
        "order":      {2},
        "escalation": {2, 3},
    }
    active_segs = seg_active_map.get(final, set()) if final in seg_active_map else set()

    def hseg_cls(seg_idx):
        return "active" if seg_idx in active_segs else ""

    # Clip class per segment — depends on which agent is active:
    # seg_0: always right-half (outer-left) — no dangle beyond chitchat
    # seg_1: right-half when RAG active (short drop); full width when Chitchat active (bridge)
    # seg_2: left-half when Order active (short drop); full width when Escalation active (bridge)
    # seg_3: always left-half (outer-right) — no dangle beyond escalation
    def hseg_clip(seg_idx):
        # Clip classes only matter when the segment IS active.
        # Inactive segments always show full grey — no clip needed.
        if seg_idx == 0: return "seg-outer-left"    # active only for chitchat; clips right-half
        if seg_idx == 1: return "seg-inner-left" if final == "rag" else ""  # rag: right-half; chitchat bridge: full
        if seg_idx == 2: return "seg-inner-right" if final == "order" else ""  # order: left-half; escalation bridge: full
        if seg_idx == 3: return "seg-outer-right"   # active only for escalation; clips left-half
        return ""

    has_result = bool(active)
    if is_processing:
        status = "Awaiting execution&hellip;"
    elif is_block:
        status = "Blocked by guardrail"
    elif has_result:
        label_map = {"rag": "RAG", "order": "Order", "escalation": "Escalation", "chitchat": "Chitchat"}
        status = f"Routed to {label_map.get(final, final)}"
    else:
        status = "Awaiting query&hellip;"

    return {
        "cls_guardrail":        node_cls("guardrail"),
        "cls_router":           node_cls("delegation_router"),
        "cls_rag":              node_cls("rag"),
        "cls_order":            node_cls("order"),
        "cls_escalation":       node_cls("escalation"),
        "cls_chitchat":         node_cls("chitchat"),
        "cls_synthesis":        node_cls("synthesis"),
        "cls_arrow_gr_dr":      arrow_cls("guardrail", "delegation_router"),
        "cls_arrow_dr_agents":  arrow_cls("delegation_router"),
        "cls_arrow_agents_syn": arrow_cls("synthesis"),
        "cls_tick_rag":         tick_cls("rag"),
        "cls_tick_order":       tick_cls("order"),
        "cls_tick_escalation":  tick_cls("escalation"),
        "cls_tick_chitchat":    tick_cls("chitchat"),
        "cls_hseg_0":           hseg_cls(0),
        "cls_hseg_1":           hseg_cls(1),
        "cls_hseg_2":           hseg_cls(2),
        "cls_hseg_3":           hseg_cls(3),
        "clip_hseg_0":          hseg_clip(0),
        "clip_hseg_1":          hseg_clip(1),
        "clip_hseg_2":          hseg_clip(2),
        "clip_hseg_3":          hseg_clip(3),
        "cls_block_label":      "show" if is_block else "",
        "cls_dot_live":         "executing" if is_processing else ("live" if has_result else ""),
        "status_label":         status,
        "cls_query_box":        "has-query" if has_result else "",
        "cls_query_arrow":      "active" if has_result else "",
        "query_text":           "",
    }


def render_agent_flow_diagram():
    active, final, is_processing = _get_flow_state()
    cls = _build_flow_classes(active, final, is_processing)

    msgs = st.session_state.get("messages", [])
    last_user = next((m for m in reversed(msgs) if m["role"] == "user"), None)
    if last_user:
        q = last_user["content"]
        cls["query_text"] = q[:80] + "…" if len(q) > 80 else q
    else:
        cls["query_text"] = "No query yet"

    panel_html = FLOW_DIAGRAM_HTML.format(**cls)
    escaped = panel_html.replace("\\", "\\\\").replace("`", "\\`")

    components.html(f"""
<script>
(function() {{
  const doc = window.parent.document;

  // Remove stale panel
  const old = doc.getElementById('af-panel-root');
  if (old) old.remove();
  const wrap = doc.createElement('div');
  wrap.id = 'af-panel-root';
  wrap.innerHTML = `{escaped}`;
  doc.body.appendChild(wrap);

  // Size the panel and keep it visually fixed regardless of horizontal scroll
  function sizePanel() {{
    const cols = doc.querySelectorAll('[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]');
    if (cols.length < 2) {{ setTimeout(sizePanel, 100); return; }}
    const rect = cols[1].getBoundingClientRect();
    const panel = doc.querySelector('.af-panel');
    if (!panel) {{ setTimeout(sizePanel, 100); return; }}
    const scrollX = window.parent.scrollX || window.parent.pageXOffset || 0;
    const absLeft = rect.left + scrollX;
    panel.style.left  = absLeft + 'px';
    panel.style.width = Math.round(rect.width) + 'px';
    panel.style.right = 'auto';

    // Align AGENT FLOW header with SHOPEASY header
    const afHeader = doc.querySelector('.af-header');
    if (afHeader) {{
      const sidebarFirst = doc.querySelector('section[data-testid="stSidebar"] .stMarkdown');
      const sidePadTop = sidebarFirst ? Math.round(sidebarFirst.getBoundingClientRect().top) : 12;
      afHeader.style.paddingTop = Math.max(sidePadTop, 4) + 'px';
    }}
  }}
  sizePanel();
  window.parent.addEventListener('resize', sizePanel);
  window.parent.addEventListener('scroll', sizePanel, true);
}})();
</script>
""", height=0)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="display:flex; align-items:center; gap:12px; padding:4px 4px 6px 4px;">
  <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#1a73e8 0%,#0d47a1 100%);display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 3px 8px rgba(26,115,232,0.4);flex-shrink:0;">🛒</div>
  <div>
    <div style="font-size:1.2rem;font-weight:900;letter-spacing:1px;line-height:1.1;">
      <span style="color:#1a73e8;">SHOP</span><span style="color:#0d47a1;">EASY</span>
    </div>
    <div style="color:#888;font-size:0.68rem;letter-spacing:1.2px;text-transform:uppercase;margin-top:2px;white-space:nowrap;">Customer Support</div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
<p style="font-style:italic;font-size:0.72rem;line-height:1.4;border-left:3px solid #1a73e8;padding-left:8px;margin:4px 0;opacity:0.75;">
Aria is your AI shopping assistant, powered by ShopEasy's knowledge base.</p>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
<div style="font-size:0.72rem;">
<strong>What I can do:</strong>
<ul style="margin-top:0.3rem;padding-left:1rem;">
  <li style="white-space:nowrap;">📦 Track orders &amp; shipments <sup style="font-size:0.58rem;color:#1a73e8;font-weight:600;">beta</sup></li>
  <li style="white-space:nowrap;">🔄 Help with returns &amp; refunds <sup style="font-size:0.58rem;color:#1a73e8;font-weight:600;">beta</sup></li>
  <li style="white-space:nowrap;">💳 Answer payment questions</li>
  <li style="white-space:nowrap;">📋 Explain store policies</li>
  <li style="white-space:nowrap;">🙋 General account help</li>
</ul>
</div>
""", unsafe_allow_html=True)
    if st.button("🗑️ Clear chat", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("""
<style>
  section[data-testid="stSidebar"] div.stButton > button {
    position: fixed; bottom: 7.5rem; width: 220px;
    white-space: nowrap !important; font-size: 0.72rem !important;
  }
  section[data-testid="stSidebar"] div.stButton > button p,
  section[data-testid="stSidebar"] div.stButton > button span {
    font-size: 0.72rem !important;
  }
</style>
<div style="position:fixed;bottom:1.2rem;width:220px;">
  <hr style="border-color:#e0e0e0;margin-bottom:0.6rem;">
  <div style="font-size:0.72rem;margin-bottom:0.6rem;text-align:center;opacity:0.85;">
    📞 <strong>Support hotline</strong><br>
    <span style="font-family:monospace;color:#1a73e8;">1800-3000-9009</span>
  </div>
  <div style="font-size:0.68rem;opacity:0.5;margin-bottom:0.6rem;text-align:center;">Powered by ShopEasy Aria · v1.0</div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def badge_html(agent_outcome: str, guardrail: str) -> str:
    if guardrail == "BLOCK":
        return '<span class="badge badge-block">⛔ blocked</span>'
    mapping = {
        "rag":        ("badge-rag",        "📚 policy"),
        "order":      ("badge-tool",       "📦 order"),
        "escalation": ("badge-escalation", "🚨 escalation"),
        "chitchat":   ("badge-chat",       "💬 chat"),
    }
    cls, label = mapping.get(agent_outcome, ("badge-chat", "💬 chat"))
    return f'<span class="badge {cls}">{label}</span>'


def md_to_html(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)
    lines = text.split('\n')
    out = []
    depth = 0  # 0 = no list, 1 = outer ul, 2 = inner ul

    def indent_level(line):
        spaces = len(line) - len(line.lstrip(' \t'))
        return spaces

    def is_bullet(line):
        return bool(re.match(r'^(\s*)[-•]\s+', line))

    def is_numbered(line):
        return bool(re.match(r'^(\s*)\d+\.\s+', line))

    def bullet_text(line):
        return re.sub(r'^(\s*)[-•]\s+', '', line).strip()

    def numbered_text(line):
        return re.sub(r'^(\s*)\d+\.\s+', '', line).strip()

    for line in lines:
        if not line.strip():
            continue
        if is_bullet(line) or is_numbered(line):
            ind = indent_level(line)
            content = bullet_text(line) if is_bullet(line) else numbered_text(line)
            if ind >= 2:  # indented — nested list item
                if depth == 0:
                    out.append('<ul>'); depth = 1
                if depth == 1:
                    out.append('<ul style="margin-top:0.15rem;">'); depth = 2
                out.append(f'<li>{content}</li>')
            else:  # top-level bullet
                if depth == 2:
                    out.append('</ul>'); depth = 1
                if depth == 0:
                    out.append('<ul>'); depth = 1
                out.append(f'<li>{content}</li>')
        else:
            # Close any open lists
            if depth == 2: out.append('</ul>'); depth = 1
            if depth == 1: out.append('</ul>'); depth = 0
            out.append(f'<p>{line.strip()}</p>')

    if depth == 2: out.append('</ul>')
    if depth == 1: out.append('</ul>')
    return ''.join(out)


def render_message(role: str, content: str, intent: str = "", guardrail: str = ""):
    if role == "user":
        st.markdown(f"""
<div class="msg-row user">
  <div class="msg-inner">
    <div class="bubble user">{content}</div>
    <div class="avatar user-av">👤</div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        badge = badge_html(intent, guardrail)
        st.markdown(f"""
<div class="msg-row assistant">
  <div class="msg-inner">
    <div class="avatar aria-av">🛍️</div>
    <div>
      <div style="font-size:0.72rem;color:#6c757d;margin-bottom:3px;">Aria{badge}</div>
      <div class="bubble assistant">{md_to_html(content)}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ── Layout: two columns ───────────────────────────────────────────────────────
SUGGESTIONS = [
    "What's your return policy?",
    "Track my order ORD-2024-001",
    "How do I pay with EMI?",
    "What are your shipping charges?",
]

chips_inner_af = "".join(f'<span class="af-chip">{s}</span>' for s in SUGGESTIONS)
chips_html = f'<div class="chips-row">{"".join(f"<span class=chip>{s}</span>" for s in SUGGESTIONS)}</div>'

col_chat, col_flow = st.columns([3, 1], gap="small")

WELCOME = "Hi! I'm Aria, your friendly customer support agent at ShopEasy! I'm here to help you with your queries to make your experience smoother."


# ── Streaming ─────────────────────────────────────────────────────────────────
def stream_response(query: str):
    try:
        with requests.post(f"{API_URL}/chat", json={"query": query}, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data:"): continue
                payload = json.loads(raw[5:].strip())
                if payload["type"] == "token":   yield payload["content"], None
                elif payload["type"] == "done":  yield "", payload
    except requests.exceptions.ConnectionError:
        yield "⚠️ Cannot reach the API. Make sure `uvicorn api:app` is running on port 8000.", {
            "type": "done", "agent_outcome": "", "guardrail_decision": ""
        }


# ── Chat column ───────────────────────────────────────────────────────────────
with col_chat:
    # Inject Aria header + chips as a fixed bar into parent document
    # This keeps it pinned at top even when the page scrolls.
    aria_header_inner = f"""
<style>
#aria-fixed-bar {{
  position: fixed; top: 0; z-index: 1000;
  padding: 8px 14px 6px 14px;
  display: flex; flex-direction: column; gap: 6px;
  /* background set dynamically by JS from stApp */
}}
.aria-hdr {{
  background: linear-gradient(135deg, #1565c0 0%, #0a2d6e 100%);
  border-radius: 10px; padding: 8px 16px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: 0 4px 14px rgba(13,71,161,0.35);
}}
.aria-hdr .logo {{ font-size: 1.4rem; }}
.aria-hdr h1 {{
  margin: 0; font-size: 1.2rem; font-weight: 900; letter-spacing: 2px; font-style: italic;
  background: linear-gradient(90deg,#e3f2fd 0%,#90caf9 60%,#fff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.aria-hdr p {{ margin: 1px 0 0; font-size: 0.68rem; color: #90caf9; }}
.af-chips-row {{ display:flex; flex-wrap:nowrap; gap:7px; overflow-x:auto; scrollbar-width:none; padding-bottom:2px; justify-content:center; }}
.af-chips-row::-webkit-scrollbar {{ display:none; }}
.af-chip {{
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 20px;
  padding: 4px 11px;
  font-size: 0.72rem;
  color: #e8eaed;
  white-space: nowrap;
  flex-shrink: 0;
  cursor: pointer;
  font-family: "Inter", "Amazon Ember", Arial, sans-serif;
  transition: background 0.2s, border-color 0.2s;
}}
.af-chip:hover {{
  background: rgba(255,153,0,0.15);
  border-color: #ff9900;
  color: #ff9900;
}}
@media (prefers-color-scheme: light) {{
  .af-chip {{
    background: #ffffff;
    border: 1px solid #c0c8d8;
    color: #1a1d24;
  }}
  .af-chip:hover {{
    background: rgba(224,112,0,0.08);
    border-color: #e07000;
    color: #e07000;
  }}
}}
</style>
<div id="aria-fixed-bar">
  <div class="aria-hdr">
    <div class="logo">🛍️</div>
    <div>
      <h1>Aria</h1>
      <p>Your ShopEasy AI assistant — ask me anything about your orders, returns, or policies.</p>
    </div>
  </div>
  <div class="af-chips-row">{chips_inner_af}</div>
</div>
"""
    escaped_header = aria_header_inner.replace("\\", "\\\\").replace("`", "\\`")
    components.html(f"""
<script>
(function() {{
  const doc = window.parent.document;
  const old = doc.getElementById('aria-bar-root');
  if (old) old.remove();
  const wrap = doc.createElement('div');
  wrap.id = 'aria-bar-root';
  wrap.innerHTML = `{escaped_header}`;
  doc.body.appendChild(wrap);

  function getAppBg() {{
    // Try stApp first (carries Streamlit theme color), then stMain, then body
    const candidates = [
      doc.querySelector('[data-testid="stApp"]'),
      doc.querySelector('[data-testid="stMain"]'),
      doc.querySelector('.main'),
      doc.body,
    ];
    for (const el of candidates) {{
      if (!el) continue;
      const bg = window.parent.getComputedStyle(el).backgroundColor;
      // Skip transparent / fully-transparent values
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') return bg;
    }}
    return '#0e1117';
  }}

  function positionBar() {{
    const cols = doc.querySelectorAll('[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]');
    if (cols.length < 1) {{ setTimeout(positionBar, 100); return; }}
    const col = cols[0];
    const bar = doc.getElementById('aria-fixed-bar');
    if (!bar) {{ setTimeout(positionBar, 100); return; }}
    // offsetLeft is scroll-independent (relative to offsetParent), not affected by scrollX
    const scrollX = window.parent.scrollX || window.parent.pageXOffset || 0;
    const rect = col.getBoundingClientRect();
    const absLeft = rect.left + scrollX;   // absolute position regardless of scroll
    bar.style.left  = absLeft + 'px';
    bar.style.width = Math.round(rect.width) + 'px';
    bar.style.background = getAppBg();
  }}

  function pinSidebar() {{
    const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
    if (!sidebar) return;
    const scrollX = window.parent.scrollX || window.parent.pageXOffset || 0;
    // Counter-scroll the sidebar so it stays visually fixed at left:0
    sidebar.style.transform = 'translateX(' + scrollX + 'px)';
  }}

  positionBar();
  pinSidebar();
  window.parent.addEventListener('resize', function() {{ positionBar(); pinSidebar(); }});
  window.parent.addEventListener('scroll', function() {{ positionBar(); pinSidebar(); }}, true);

  // Pin chat input so it never scrolls away, aligned to chat column
  const styleId = 'aria-input-pin';
  if (!doc.getElementById(styleId)) {{
    const s = doc.createElement('style');
    s.id = styleId;
    s.textContent = `
      div[data-testid="stBottom"],
      .stChatFloatingInputContainer {{
        position: fixed !important;
        bottom: 0 !important;
        z-index: 999 !important;
        background: transparent !important;
      }}
    `;
    doc.head.appendChild(s);
  }}

  function pinInput() {{
    const cols = doc.querySelectorAll('[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]');
    if (cols.length < 1) {{ setTimeout(pinInput, 150); return; }}
    const col = cols[0];
    const rect = col.getBoundingClientRect();
    const scrollX = window.parent.scrollX || window.parent.pageXOffset || 0;
    const absLeft = rect.left + scrollX;
    const targets = doc.querySelectorAll('div[data-testid="stBottom"], .stChatFloatingInputContainer');
    targets.forEach(function(el) {{
      el.style.left  = absLeft + 'px';
      el.style.width = Math.round(rect.width) + 'px';
    }});
  }}
  pinInput();
  window.parent.addEventListener('resize', pinInput);
  window.parent.addEventListener('scroll', pinInput, true);
  // Re-run periodically to catch Streamlit re-renders that recreate the element
  setInterval(pinInput, 800);
}})();
</script>
""", height=0)

    # Spacer so messages start below the fixed header bar (~115px)
    st.markdown('<div style="height:115px"></div>', unsafe_allow_html=True)

    # Scrollable message area
    chat_container = st.container(height=480, border=False)
    with chat_container:
        if not st.session_state.messages:
            render_message("assistant", WELCOME)
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"],
                           msg.get("agent_outcome", ""), msg.get("guardrail", ""))

    # Chat input
    if prompt := st.chat_input("Ask Aria anything about ShopEasy…"):
        st.session_state.processing = True
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Re-render flow diagram immediately to show idle state while streaming
        with col_flow:
            render_agent_flow_diagram()
        with chat_container:
            render_message("user", prompt)
            placeholder = st.empty()

        placeholder.markdown("""
<style>
@keyframes blink { 0%,100%{opacity:0.2;} 50%{opacity:1;} }
.dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#1565c0;margin:0 2px;animation:blink 1.2s infinite;}
.dot:nth-child(2){animation-delay:0.2s;} .dot:nth-child(3){animation-delay:0.4s;}
</style>
<div class="msg-row assistant"><div class="msg-inner">
  <div class="avatar aria-av">🛍️</div>
  <div>
    <div style="font-size:0.72rem;color:#6c757d;margin-bottom:3px;">Aria</div>
    <div class="bubble assistant" style="display:inline-flex;align-items:center;padding:10px 16px;">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
  </div>
</div></div>""", unsafe_allow_html=True)

        accumulated = ""
        intent_val = ""
        guardrail_val = ""

        for token, meta in stream_response(prompt):
            if meta is not None:
                intent_val    = meta.get("agent_outcome", "")
                guardrail_val = meta.get("guardrail_decision", "")
            else:
                accumulated += token
                placeholder.markdown(f"""
<div class="msg-row assistant"><div class="msg-inner">
  <div class="avatar aria-av">🛍️</div>
  <div>
    <div style="font-size:0.72rem;color:#6c757d;margin-bottom:3px;">Aria</div>
    <div class="bubble assistant">{accumulated}▌</div>
  </div>
</div></div>""", unsafe_allow_html=True)

        badge = badge_html(intent_val, guardrail_val)
        placeholder.markdown(f"""
<div class="msg-row assistant"><div class="msg-inner">
  <div class="avatar aria-av">🛍️</div>
  <div>
    <div style="font-size:0.72rem;color:#6c757d;margin-bottom:3px;">Aria{badge}</div>
    <div class="bubble assistant">{md_to_html(accumulated)}</div>
  </div>
</div></div>""", unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant", "content": accumulated,
            "agent_outcome": intent_val, "guardrail": guardrail_val,
        })
        st.session_state.processing = False
        st.rerun()

    components.html("""
<script>
  function init() {
    const doc = window.parent.document;
    const el = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
    if (el) el.focus();
    else setTimeout(init, 150);
  }
  init();
</script>
""", height=0)


# ── Flow diagram column ───────────────────────────────────────────────────────
with col_flow:
    render_agent_flow_diagram()
