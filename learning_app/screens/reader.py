import tkinter as tk
from tkinter import ttk
from db import get_topic_by_id


class ReaderScreen(tk.Frame):
    def __init__(self, parent, on_back, on_chat):
        super().__init__(parent, bg="#ffffff")
        self.on_back = on_back
        self.on_chat = on_chat
        self.topic_id = None
        self._build()

    def _build(self):
        # Top bar
        top = tk.Frame(self, bg="#2b6cb0")
        top.pack(fill="x")

        ttk.Button(top, text="← Back", command=self.on_back).pack(side="left", padx=10, pady=8)
        self.title_var = tk.StringVar()
        tk.Label(top, textvariable=self.title_var, font=("Helvetica", 14, "bold"),
                 bg="#2b6cb0", fg="white").pack(side="left", padx=10)
        ttk.Button(top, text="Ask AI about this →",
                   command=self._go_chat).pack(side="right", padx=10, pady=8)

        # Meta info
        self.meta_var = tk.StringVar()
        tk.Label(self, textvariable=self.meta_var, font=("Helvetica", 9),
                 bg="#ffffff", fg="#718096").pack(anchor="w", padx=15, pady=(6, 0))

        # Content area
        content_frame = tk.Frame(self, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        scrollbar = ttk.Scrollbar(content_frame, orient="vertical")
        self.text_area = tk.Text(content_frame, font=("Georgia", 12), wrap="word",
                                 yscrollcommand=scrollbar.set,
                                 bg="#ffffff", fg="#2d3748", bd=0,
                                 padx=10, pady=10, state="disabled")
        scrollbar.config(command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)

    def load(self, topic_id):
        self.topic_id = topic_id
        row = get_topic_by_id(topic_id)
        if not row:
            return
        tid, name, content, url, saved_at = row
        self.title_var.set(name)
        self.meta_var.set(f"Source: {url}   |   Saved: {saved_at[:16]}")
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)
        self.text_area.config(state="disabled")
        self.text_area.yview_moveto(0)

    def _go_chat(self):
        if self.topic_id is not None:
            self.on_chat(self.topic_id)
