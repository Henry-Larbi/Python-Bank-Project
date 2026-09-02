import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ──────────────────────────────────────────────
# DIAGRAM 1 — APP FLOW
# ──────────────────────────────────────────────
def draw_box(ax, x, y, w, h, text, bg, fg="white", fontsize=11, radius=0.06):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=f"round,pad={radius}",
                         facecolor=bg, edgecolor="white", linewidth=2, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=fg, fontweight="bold", zorder=4, wrap=True,
            multialignment="center")

def arrow(ax, x1, y1, x2, y2, color="#94a3b8"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=2, mutation_scale=18), zorder=2)

fig1, ax1 = plt.subplots(figsize=(13, 16))
ax1.set_xlim(0, 13)
ax1.set_ylim(0, 16)
ax1.axis("off")
fig1.patch.set_facecolor("#0f172a")
ax1.set_facecolor("#0f172a")

ax1.text(6.5, 15.3, "Learning App — Flow Diagram", ha="center", va="center",
         fontsize=18, color="white", fontweight="bold")

# ── Row 1: Entry ──
draw_box(ax1, 6.5, 14.3, 4.5, 0.9, "HOME SCREEN\nSearch bar · Saved topics list", "#1e40af")

# ── Row 2: Scrape ──
draw_box(ax1, 6.5, 12.8, 4.5, 0.9, "SCRAPE ENGINE (scraper.py)\nrequests + BeautifulSoup4", "#7c3aed")
arrow(ax1, 6.5, 13.85, 6.5, 13.25)

# ── Row 3: Sources side by side ──
draw_box(ax1, 3.5, 11.3, 3.2, 0.85, "Wikipedia\nen.wikipedia.org", "#0f766e", fontsize=10)
draw_box(ax1, 9.5, 11.3, 3.2, 0.85, "GeeksForGeeks\ngeeksforgeeks.org", "#0f766e", fontsize=10)
arrow(ax1, 5.0, 12.35, 3.8, 11.72)
arrow(ax1, 8.0, 12.35, 9.2, 11.72)

ax1.text(6.5, 11.3, "fallback →", ha="center", va="center",
         fontsize=9, color="#94a3b8", style="italic")

# ── Row 4: Storage ──
draw_box(ax1, 6.5, 9.8, 4.5, 0.9, "STORAGE  (db.py · SQLite)\ntopic · content · source URL · date", "#b45309")
arrow(ax1, 3.5, 10.87, 5.5, 10.25)
arrow(ax1, 9.5, 10.87, 7.5, 10.25)

# ── Row 5: Two branches ──
draw_box(ax1, 3.0, 8.2, 3.8, 0.9, "READER SCREEN\nDisplay full content\nScroll · Save · Delete", "#1d4ed8", fontsize=10)
draw_box(ax1, 10.0, 8.2, 3.8, 0.9, "AI CHAT SCREEN\nAsk questions\nAI answers from content", "#065f46", fontsize=10)
arrow(ax1, 5.0, 9.35, 3.8, 8.65)
arrow(ax1, 8.0, 9.35, 9.2, 8.65)

# ── Row 6: AI backend ──
draw_box(ax1, 10.0, 6.6, 3.8, 0.9, "Anthropic API  (ai_chat.py)\nClaude Haiku model", "#7c3aed", fontsize=10)
arrow(ax1, 10.0, 7.75, 10.0, 7.05)

# ── Row 7: Chat history ──
draw_box(ax1, 10.0, 5.1, 3.8, 0.9, "Chat History\nSaved in SQLite\nPersists across sessions", "#b45309", fontsize=10)
arrow(ax1, 10.0, 6.15, 10.0, 5.55)

# ── Legend ──
legend_items = [
    ("#1e40af", "UI Screen"),
    ("#7c3aed", "Logic / AI"),
    ("#0f766e", "Web Source"),
    ("#b45309", "Database"),
    ("#065f46", "AI Chat"),
]
for i, (color, label) in enumerate(legend_items):
    bx = 0.6 + i * 2.5
    patch = FancyBboxPatch((bx, 0.3), 2.0, 0.55, boxstyle="round,pad=0.05",
                           facecolor=color, edgecolor="white", linewidth=1.2)
    ax1.add_patch(patch)
    ax1.text(bx + 1.0, 0.575, label, ha="center", va="center",
             fontsize=9, color="white", fontweight="bold")

ax1.text(6.5, 0.1, "Flow: User → Scrape → Store → Read / Chat with AI",
         ha="center", va="center", fontsize=9, color="#94a3b8", style="italic")

plt.tight_layout()
fig1.savefig("/home/user/Python-Bank-Project/learning_app/app_flow.png",
             dpi=150, bbox_inches="tight", facecolor=fig1.get_facecolor())
plt.close(fig1)
print("app_flow.png saved")


# ──────────────────────────────────────────────
# DIAGRAM 2 — MODULE ROADMAP
# ──────────────────────────────────────────────
modules = [
    {
        "step": "01",
        "name": "requests",
        "tagline": "Fetch web pages",
        "skills": ["requests.get(url)", "response.status_code", "response.text", "headers & timeout"],
        "color": "#1d4ed8",
        "time": "2–3 days",
    },
    {
        "step": "02",
        "name": "BeautifulSoup4",
        "tagline": "Parse & extract HTML",
        "skills": ["BeautifulSoup(html, parser)", "soup.select(css)", "tag.get_text()", "find() / find_all()"],
        "color": "#7c3aed",
        "time": "3–4 days",
    },
    {
        "step": "03",
        "name": "sqlite3",
        "tagline": "Store data locally",
        "skills": ["connect() / cursor()", "CREATE TABLE / INSERT", "SELECT / fetchall()", "commit() / close()"],
        "color": "#b45309",
        "time": "3–4 days",
    },
    {
        "step": "04",
        "name": "tkinter",
        "tagline": "Build the desktop GUI",
        "skills": ["Label / Entry / Button", "Frame / Text widget", ".pack() / .grid()", "Events & callbacks"],
        "color": "#0f766e",
        "time": "5–7 days",
    },
    {
        "step": "05",
        "name": "threading",
        "tagline": "Keep GUI responsive",
        "skills": ["Thread(target=fn)", "daemon=True", "after() for GUI updates", "Avoid blocking mainloop"],
        "color": "#92400e",
        "time": "1–2 days",
    },
    {
        "step": "06",
        "name": "anthropic",
        "tagline": "Add AI tutoring",
        "skills": ["Anthropic() client", "messages.create()", "System prompt + context", "Chat history format"],
        "color": "#be185d",
        "time": "2–3 days",
    },
]

fig2, ax2 = plt.subplots(figsize=(14, 17))
ax2.set_xlim(0, 14)
ax2.set_ylim(0, 17)
ax2.axis("off")
fig2.patch.set_facecolor("#0f172a")
ax2.set_facecolor("#0f172a")

ax2.text(7, 16.4, "Module Learning Roadmap", ha="center", va="center",
         fontsize=20, color="white", fontweight="bold")
ax2.text(7, 15.9, "Master these 6 modules to build the Learning App",
         ha="center", va="center", fontsize=12, color="#94a3b8", style="italic")

card_h = 2.2
gap = 0.25
start_y = 15.3

for i, mod in enumerate(modules):
    y_top = start_y - i * (card_h + gap)
    y_center = y_top - card_h / 2

    # Card background
    card = FancyBboxPatch((0.5, y_top - card_h), 13, card_h,
                          boxstyle="round,pad=0.1",
                          facecolor=mod["color"] + "22",
                          edgecolor=mod["color"], linewidth=2, zorder=2)
    ax2.add_patch(card)

    # Step badge
    badge = FancyBboxPatch((0.7, y_top - card_h + 0.35), 1.1, 1.45,
                           boxstyle="round,pad=0.08",
                           facecolor=mod["color"], edgecolor="white",
                           linewidth=1.5, zorder=3)
    ax2.add_patch(badge)
    ax2.text(1.25, y_center, mod["step"], ha="center", va="center",
             fontsize=22, color="white", fontweight="bold", zorder=4)

    # Module name & tagline
    ax2.text(2.3, y_top - 0.45, mod["name"],
             fontsize=15, color=mod["color"], fontweight="bold", va="top", zorder=3)
    ax2.text(2.3, y_top - 0.95, mod["tagline"],
             fontsize=11, color="#cbd5e0", va="top", style="italic", zorder=3)

    # Skills list
    for j, skill in enumerate(mod["skills"]):
        col = 2.3 + (j % 2) * 4.8
        row_y = y_top - 1.5 - (j // 2) * 0.45
        ax2.text(col, row_y, f"▸  {skill}", fontsize=9.5,
                 color="#e2e8f0", va="top", zorder=3, family="monospace")

    # Time badge
    time_box = FancyBboxPatch((11.2, y_top - 0.85), 2.1, 0.6,
                              boxstyle="round,pad=0.08",
                              facecolor=mod["color"], edgecolor="white",
                              linewidth=1, zorder=3)
    ax2.add_patch(time_box)
    ax2.text(12.25, y_top - 0.55, f"~ {mod['time']}",
             ha="center", va="center", fontsize=9, color="white",
             fontweight="bold", zorder=4)

    # Arrow to next card
    if i < len(modules) - 1:
        ax2.annotate("", xy=(7, y_top - card_h - gap + 0.01),
                     xytext=(7, y_top - card_h - 0.01),
                     arrowprops=dict(arrowstyle="-|>", color="#475569",
                                     lw=2, mutation_scale=16), zorder=1)

# Footer
ax2.text(7, 0.25, "Total estimated time: 16–23 days of practice",
         ha="center", va="center", fontsize=11, color="#94a3b8", style="italic")

plt.tight_layout()
fig2.savefig("/home/user/Python-Bank-Project/learning_app/module_roadmap.png",
             dpi=150, bbox_inches="tight", facecolor=fig2.get_facecolor())
plt.close(fig2)
print("module_roadmap.png saved")
