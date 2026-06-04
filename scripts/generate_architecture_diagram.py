"""
Generates architecture_diagram.png in the project root.
Run with:  uv run python scripts/generate_architecture_diagram.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(14, 12))
ax.set_xlim(0, 14)
ax.set_ylim(0, 12)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")


# ── helpers ──────────────────────────────────────────────────────────────────

def box(ax, x, y, w, h, fc, ec, lw=1.5, radius=0.35, zorder=2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=zorder,
    ))


def txt(ax, x, y, s, fs=9, color="#1a1a1a", bold=False, ha="center", va="center",
        italic=False, zorder=6):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, zorder=zorder,
            fontweight="bold" if bold else "normal",
            fontstyle="italic" if italic else "normal")


def arrow(ax, x1, y1, x2, y2, color="#555555", lw=1.6, dashed=False, head=0.22):
    ls = (0, (4, 3)) if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle=f"->,head_width={head},head_length=0.15",
                    color=color, lw=lw, linestyle=ls),
                zorder=5)


def inner(ax, x, y, w, h, fc, ec, label, fs=8.6):
    box(ax, x, y, w, h, fc, ec, lw=1.1, radius=0.2, zorder=4)
    txt(ax, x + w/2, y + h/2, label, fs=fs, zorder=6)


# ── palette ───────────────────────────────────────────────────────────────────
SUP_BG,   SUP_EC   = "#eae8f7", "#9b8ec4"
GRD_BG,   GRD_EC   = "#fce8e8", "#e08080"
DEL_BG,   DEL_EC   = "#fef3e2", "#d4a03a"
RAG_BG,   RAG_EC   = "#e6f4ea", "#4caf50"
RAG_IB,   RAG_IEB  = "#c8e6c9", "#388e3c"
ORD_BG,   ORD_EC   = "#fff8e1", "#f9a825"
ORD_IB,   ORD_IEB  = "#ffecb3", "#f57f17"
ESC_BG,   ESC_EC   = "#fce4ec", "#e91e63"
ESC_IB,   ESC_IEB  = "#f8bbd0", "#c2185b"
CHAT_BG,  CHAT_EC  = "#e3f2fd", "#1976d2"
SYN_BG,   SYN_EC   = "#ede7f6", "#7b1fa2"
USR_BG,   USR_EC   = "#f0f0f0", "#aaaaaa"
ARW       = "#444444"
ARW_D     = "#999999"


# ── 1. User query ─────────────────────────────────────────────────────────────
box(ax, 5.25, 10.85, 3.5, 0.75, USR_BG, USR_EC, lw=1.2)
txt(ax, 7.0, 11.22, "User query", fs=11, bold=True)
arrow(ax, 7.0, 10.85, 7.0, 9.95, ARW)


# ── 2. Supervisor agent ───────────────────────────────────────────────────────
box(ax, 0.5, 8.25, 13.0, 1.55, SUP_BG, SUP_EC, lw=2.0, radius=0.45)
txt(ax, 3.2, 9.52, "Supervisor agent", fs=10.5, bold=True, ha="center")
txt(ax, 3.2, 9.2,  "Own graph · own state · orchestrates sub-agents",
    fs=7.6, color="#555555", ha="center")

# guardrail inner
inner(ax, 0.85, 8.44, 2.9, 0.88, GRD_BG, GRD_EC,
      "Guardrail\nSafety + scope", fs=9)
# delegation router inner
inner(ax, 5.1, 8.44, 4.2, 0.88, DEL_BG, DEL_EC,
      "Delegation router\nWhich agent handles this?", fs=9)

# guardrail -> delegation router
arrow(ax, 3.75, 8.88, 5.1, 8.88, ARW)


# ── 3. Chitchat (inline, below supervisor left) ───────────────────────────────
box(ax, 0.5, 6.3, 2.6, 1.8, CHAT_BG, CHAT_EC, lw=1.6, radius=0.35)
txt(ax, 1.8, 7.75, "Chitchat", fs=10, bold=True, color="#0d47a1")
txt(ax, 1.8, 7.44, "inline · supervisor node", fs=7.5, color="#1565c0")
txt(ax, 1.8, 7.14, "no sub-graph", fs=7.2, color="#555555")
inner(ax, 0.68, 6.46, 2.24, 0.52, CHAT_BG, CHAT_EC, "chitchat_node", fs=8.2)

# supervisor -> chitchat
arrow(ax, 1.8, 8.25, 1.8, 8.1, ARW)


# ── 4. RAG agent ──────────────────────────────────────────────────────────────
box(ax, 3.4, 3.85, 3.2, 4.15, RAG_BG, RAG_EC, lw=2.0, radius=0.4)
txt(ax, 3.65, 7.68, "RAG agent", fs=10, bold=True, color="#1b5e20", ha="left")
txt(ax, 3.65, 7.38, "Own graph + state", fs=7.6, color="#2e7d32", ha="left")

inner(ax, 3.6, 6.3,  2.8, 0.65, RAG_IB, RAG_IEB, "rag_node  (ChromaDB top-3)")
inner(ax, 3.6, 5.3,  2.8, 0.65, RAG_IB, RAG_IEB, "response_generator")
txt(ax,  5.0, 4.88, "outputs agent_response", fs=7.2, color="#2e7d32", italic=True)

arrow(ax, 5.0, 6.3,  5.0, 6.1,  ARW, lw=1.2, head=0.14)
arrow(ax, 5.0, 5.3,  5.0, 5.1,  ARW, lw=1.2, head=0.14)

# supervisor -> RAG
arrow(ax, 5.0, 8.25, 5.0, 8.0, ARW)


# ── 5. Order agent ────────────────────────────────────────────────────────────
box(ax, 6.9, 3.85, 3.2, 4.15, ORD_BG, ORD_EC, lw=2.0, radius=0.4)
txt(ax, 7.15, 7.68, "Order agent", fs=10, bold=True, color="#e65100", ha="left")
txt(ax, 7.15, 7.38, "Own graph + state", fs=7.6, color="#ef6c00", ha="left")

inner(ax, 7.1, 6.3,  2.8, 0.65, ORD_IB, ORD_IEB, "tool_call_node")
inner(ax, 7.1, 5.3,  2.8, 0.65, ORD_IB, ORD_IEB, "response_generator")
txt(ax,  8.5, 4.88, "outputs agent_response", fs=7.2, color="#ef6c00", italic=True)

txt(ax, 8.5, 6.06, "order status · tracking\nreturns · account info",
    fs=7.0, color="#6d4c00", italic=True)

arrow(ax, 8.5, 6.3,  8.5, 6.1,  ARW, lw=1.2, head=0.14)
arrow(ax, 8.5, 5.3,  8.5, 5.1,  ARW, lw=1.2, head=0.14)

# supervisor -> Order
arrow(ax, 8.5, 8.25, 8.5, 8.0, ARW)


# ── 6. Escalation agent ───────────────────────────────────────────────────────
box(ax, 10.4, 3.65, 3.1, 4.55, ESC_BG, ESC_EC, lw=2.0, radius=0.4)
txt(ax, 10.65, 7.68, "Escalation agent", fs=10, bold=True, color="#880e4f", ha="left")
txt(ax, 10.65, 7.38, "Own graph + state", fs=7.6, color="#ad1457", ha="left")

inner(ax, 10.6, 6.3,  2.7, 0.65, ESC_IB, ESC_IEB, "complaint_handler")
inner(ax, 10.6, 5.3,  2.7, 0.65, ESC_IB, ESC_IEB, "human_handoff")
inner(ax, 10.6, 4.3,  2.7, 0.65, ESC_IB, ESC_IEB, "ticket_creation")
txt(ax,  11.95, 3.92, "outputs agent_response", fs=7.2, color="#ad1457", italic=True)

arrow(ax, 11.95, 6.3,  11.95, 6.1,  ARW, lw=1.2, head=0.14)
arrow(ax, 11.95, 5.3,  11.95, 5.1,  ARW, lw=1.2, head=0.14)
arrow(ax, 11.95, 4.3,  11.95, 4.1,  ARW, lw=1.2, head=0.14)

# supervisor -> Escalation
arrow(ax, 11.95, 8.25, 11.95, 8.0, ARW)


# ── 7. "results" dashed arrows -> synthesis ───────────────────────────────────
txt(ax, 0.58, 3.52, "results", fs=8, color="#999999", italic=True, ha="left")

arrow(ax, 1.8,  6.3,  5.2,  3.28, ARW_D, lw=1.3, dashed=True, head=0.17)  # chitchat
arrow(ax, 5.0,  3.85, 5.8,  3.28, ARW_D, lw=1.3, dashed=True, head=0.17)  # RAG
arrow(ax, 8.5,  3.85, 7.5,  3.28, ARW_D, lw=1.3, dashed=True, head=0.17)  # Order
arrow(ax, 11.95, 3.65, 8.2, 3.28, ARW_D, lw=1.3, dashed=True, head=0.17)  # Escalation


# ── 8. Supervisor synthesis ───────────────────────────────────────────────────
box(ax, 4.0, 1.85, 6.0, 1.25, SYN_BG, SYN_EC, lw=2.0, radius=0.4)
txt(ax, 7.0, 2.72, "Supervisor synthesis", fs=11.5, bold=True, color="#4a148c")
txt(ax, 7.0, 2.32, "Merge + faithfulness check  (RAG path only)", fs=8.5, color="#6a1b9a")


# ── 9. caption ────────────────────────────────────────────────────────────────
txt(ax, 7.0, 0.55, "ShopEasy · Aria — Multi-Agent Architecture",
    fs=8.5, color="#bbbbbb", italic=True)


plt.tight_layout(pad=0.2)
out = "architecture_diagram.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="#ffffff")
print(f"Saved: {out}")
