import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scraper import fetch_topic
from db import save_topic, get_all_topics, search_topics, delete_topic


class HomeScreen(tk.Frame):
    def __init__(self, parent, on_open_topic):
        super().__init__(parent, bg="#f0f4f8")
        self.on_open_topic = on_open_topic
        self._build()
        self.load_topics()

    def _build(self):
        # Title
        tk.Label(self, text="Learning App", font=("Helvetica", 20, "bold"),
                 bg="#f0f4f8", fg="#2d3748").pack(pady=(20, 5))
        tk.Label(self, text="Search any topic to learn about it",
                 font=("Helvetica", 11), bg="#f0f4f8", fg="#718096").pack()

        # Search bar
        search_frame = tk.Frame(self, bg="#f0f4f8")
        search_frame.pack(pady=15, padx=30, fill="x")

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                                      font=("Helvetica", 13), width=35)
        self.search_entry.pack(side="left", ipady=6, expand=True, fill="x")
        self.search_entry.bind("<Return>", lambda e: self.on_fetch())

        ttk.Button(search_frame, text="Fetch & Learn",
                   command=self.on_fetch).pack(side="left", padx=(8, 0))

        # Filter saved topics
        filter_frame = tk.Frame(self, bg="#f0f4f8")
        filter_frame.pack(padx=30, fill="x")

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *a: self.filter_topics())
        ttk.Entry(filter_frame, textvariable=self.filter_var,
                  font=("Helvetica", 11), width=25).pack(side="left", ipady=4)
        tk.Label(filter_frame, text=" ← filter saved topics",
                 bg="#f0f4f8", fg="#718096", font=("Helvetica", 10)).pack(side="left")

        # Saved topics list
        tk.Label(self, text="Saved Topics", font=("Helvetica", 13, "bold"),
                 bg="#f0f4f8", fg="#2d3748").pack(anchor="w", padx=30, pady=(12, 2))

        list_frame = tk.Frame(self, bg="#f0f4f8")
        list_frame.pack(padx=30, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.topic_list = tk.Listbox(list_frame, font=("Helvetica", 12),
                                     yscrollcommand=scrollbar.set,
                                     selectbackground="#4299e1", activestyle="none",
                                     height=14, bd=0, highlightthickness=1,
                                     highlightcolor="#cbd5e0")
        scrollbar.config(command=self.topic_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.topic_list.pack(side="left", fill="both", expand=True)
        self.topic_list.bind("<Double-Button-1>", lambda e: self.open_selected())

        # Buttons row
        btn_frame = tk.Frame(self, bg="#f0f4f8")
        btn_frame.pack(pady=10, padx=30, fill="x")
        ttk.Button(btn_frame, text="Open", command=self.open_selected).pack(side="left")
        ttk.Button(btn_frame, text="Delete", command=self.delete_selected).pack(side="left", padx=8)

        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg="#f0f4f8",
                 fg="#e53e3e", font=("Helvetica", 10)).pack(pady=(0, 10))

        self._topic_ids = []

    def load_topics(self, rows=None):
        self.topic_list.delete(0, "end")
        self._topic_ids = []
        rows = rows or get_all_topics()
        for row in rows:
            tid, name, url, saved_at = row
            display = f"{name}   ({saved_at[:10]})"
            self.topic_list.insert("end", display)
            self._topic_ids.append(tid)

    def filter_topics(self):
        keyword = self.filter_var.get().strip()
        rows = search_topics(keyword) if keyword else get_all_topics()
        self.load_topics(rows)

    def on_fetch(self):
        topic = self.search_var.get().strip()
        if not topic:
            return
        self.status_var.set(f"Fetching '{topic}'...")
        self.after(50, lambda: self._fetch_thread(topic))

    def _fetch_thread(self, topic):
        def run():
            content, url = fetch_topic(topic)
            if content:
                tid = save_topic(topic, content, url)
                self.after(0, lambda: self._on_fetch_done(tid, topic))
            else:
                self.after(0, lambda: self.status_var.set(
                    f"Could not fetch '{topic}'. Try a different keyword."))
        threading.Thread(target=run, daemon=True).start()

    def _on_fetch_done(self, tid, topic):
        self.status_var.set("")
        self.search_var.set("")
        self.load_topics()
        self.on_open_topic(tid)

    def open_selected(self):
        sel = self.topic_list.curselection()
        if not sel:
            return
        self.on_open_topic(self._topic_ids[sel[0]])

    def delete_selected(self):
        sel = self.topic_list.curselection()
        if not sel:
            return
        name = self.topic_list.get(sel[0])
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            delete_topic(self._topic_ids[sel[0]])
            self.load_topics()
