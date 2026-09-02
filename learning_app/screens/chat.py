import tkinter as tk
from tkinter import ttk
import threading
from db import get_topic_by_id, get_chat_history, save_chat_message
from ai_chat import ask_ai


class ChatScreen(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg="#f7fafc")
        self.on_back = on_back
        self.topic_id = None
        self.topic_content = ""
        self.topic_name = ""
        self._build()

    def _build(self):
        # Top bar
        top = tk.Frame(self, bg="#276749")
        top.pack(fill="x")
        ttk.Button(top, text="← Back to Reader", command=self.on_back).pack(side="left", padx=10, pady=8)
        self.title_var = tk.StringVar(value="AI Chat")
        tk.Label(top, textvariable=self.title_var, font=("Helvetica", 14, "bold"),
                 bg="#276749", fg="white").pack(side="left", padx=10)

        # Chat history display
        chat_frame = tk.Frame(self, bg="#f7fafc")
        chat_frame.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical")
        self.chat_area = tk.Text(chat_frame, font=("Helvetica", 12), wrap="word",
                                 yscrollcommand=scrollbar.set,
                                 bg="#f7fafc", fg="#2d3748", bd=0,
                                 padx=10, pady=10, state="disabled")
        scrollbar.config(command=self.chat_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_area.pack(side="left", fill="both", expand=True)

        self.chat_area.tag_config("user_label", foreground="#2b6cb0", font=("Helvetica", 11, "bold"))
        self.chat_area.tag_config("ai_label", foreground="#276749", font=("Helvetica", 11, "bold"))
        self.chat_area.tag_config("user_msg", foreground="#2d3748", font=("Helvetica", 12))
        self.chat_area.tag_config("ai_msg", foreground="#1a202c", font=("Georgia", 12))

        # Input row
        input_frame = tk.Frame(self, bg="#f7fafc")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var,
                                     font=("Helvetica", 13), width=40)
        self.input_entry.pack(side="left", ipady=7, expand=True, fill="x")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg="#f7fafc",
                 fg="#718096", font=("Helvetica", 10)).pack(pady=(0, 5))

    def load(self, topic_id):
        self.topic_id = topic_id
        row = get_topic_by_id(topic_id)
        if not row:
            return
        _, name, content, _, _ = row
        self.topic_name = name
        self.topic_content = content
        self.title_var.set(f"AI Chat  —  {name}")
        self._refresh_chat()

    def _refresh_chat(self):
        self.chat_area.config(state="normal")
        self.chat_area.delete("1.0", "end")
        history = get_chat_history(self.topic_id)
        for role, message in history:
            if role == "user":
                self.chat_area.insert("end", "You:\n", "user_label")
                self.chat_area.insert("end", message + "\n\n", "user_msg")
            else:
                self.chat_area.insert("end", "AI Tutor:\n", "ai_label")
                self.chat_area.insert("end", message + "\n\n", "ai_msg")
        self.chat_area.config(state="disabled")
        self.chat_area.yview_moveto(1.0)

    def send_message(self):
        question = self.input_var.get().strip()
        if not question or not self.topic_id:
            return
        self.input_var.set("")
        self.send_btn.config(state="disabled")
        self.status_var.set("AI is thinking...")

        save_chat_message(self.topic_id, "user", question)
        self._refresh_chat()

        history = get_chat_history(self.topic_id)[:-1]  # exclude the one just saved

        def run():
            try:
                reply = ask_ai(self.topic_name, self.topic_content, history, question)
            except Exception as e:
                reply = f"[Error contacting AI: {e}]"
            save_chat_message(self.topic_id, "assistant", reply)
            self.after(0, self._on_reply)

        threading.Thread(target=run, daemon=True).start()

    def _on_reply(self):
        self.status_var.set("")
        self.send_btn.config(state="normal")
        self._refresh_chat()
        self.input_entry.focus()
