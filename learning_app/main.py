import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from db import init_db
from screens.home import HomeScreen
from screens.reader import ReaderScreen
from screens.chat import ChatScreen


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Learning App")
        self.geometry("820x620")
        self.minsize(680, 500)
        self.configure(bg="#f0f4f8")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("TEntry", font=("Helvetica", 12))

        self._container = tk.Frame(self)
        self._container.pack(fill="both", expand=True)

        self.home = HomeScreen(self._container, on_open_topic=self.show_reader)
        self.reader = ReaderScreen(self._container, on_back=self.show_home, on_chat=self.show_chat)
        self.chat = ChatScreen(self._container, on_back=self._back_to_reader)

        self._current_topic_id = None
        self.show_home()

    def show_home(self):
        self._switch(self.home)
        self.home.load_topics()

    def show_reader(self, topic_id):
        self._current_topic_id = topic_id
        self.reader.load(topic_id)
        self._switch(self.reader)

    def show_chat(self, topic_id):
        self._current_topic_id = topic_id
        self.chat.load(topic_id)
        self._switch(self.chat)

    def _back_to_reader(self):
        self.show_reader(self._current_topic_id)

    def _switch(self, frame):
        for child in self._container.winfo_children():
            child.pack_forget()
        frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
