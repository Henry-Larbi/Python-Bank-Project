import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import re
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

import db
import config


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16))

        # Header
        root.add_widget(MDLabel(
            text="Access Bank",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(80),
        ))
        root.add_widget(MDLabel(
            text="Sign in to your account",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30),
        ))

        # Fields
        self.email_field = MDTextField(
            hint_text="Email address",
            icon_right="email",
            size_hint_y=None,
            height=dp(56),
        )
        self.password_field = MDTextField(
            hint_text="Password",
            icon_right="eye-off",
            password=True,
            size_hint_y=None,
            height=dp(56),
        )
        root.add_widget(self.email_field)
        root.add_widget(self.password_field)

        # Login button
        btn_login = MDRaisedButton(
            text="SIGN IN",
            size_hint_x=1,
            height=dp(48),
            md_bg_color=App.get_running_app().theme_cls.primary_color
            if App.get_running_app() else (0.2, 0.6, 0.2, 1),
        )
        btn_login.bind(on_release=self._handle_login)
        root.add_widget(btn_login)

        # Register link
        btn_reg = MDFlatButton(
            text="Don't have an account? Register",
            size_hint_x=1,
        )
        btn_reg.bind(on_release=lambda x: setattr(
            App.get_running_app().sm, 'current', 'register'))
        root.add_widget(btn_reg)

        self.add_widget(root)

    def _show_dialog(self, title, text):
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(title=title, text=text,
                                buttons=[MDFlatButton(text="OK",
                                         on_release=lambda x: self._dialog.dismiss())])
        self._dialog.open()

    def _handle_login(self, *args):
        email    = self.email_field.text.strip()
        password = self.password_field.text.strip()

        if not email or not password:
            self._show_dialog("Missing Fields", "Please enter your email and password.")
            return

        # Admin check
        if email == config.ADMIN_EMAIL and password == config.ADMIN_PASSWORD:
            self._show_dialog("Admin", "Admin panel is only available on the desktop app.")
            return

        if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", email):
            self._show_dialog("Invalid Email", "Please enter a valid email address.")
            return

        try:
            matched = db.login(email, password)
        except Exception as e:
            self._show_dialog("Connection Error",
                f"Could not connect to the database.\nCheck your internet connection.\n\n{e}")
            return

        if matched:
            self.email_field.text = ""
            self.password_field.text = ""
            App.get_running_app().go_to("dashboard", user_email=email)
        else:
            self._show_dialog("Login Failed",
                "Invalid email or password.\nPlease try again or create an account.")
