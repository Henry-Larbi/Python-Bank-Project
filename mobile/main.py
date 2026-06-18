import sys
import os

# Allow importing db and config from parent directory
sys.path.insert(0, os.path.dirname(__file__))

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window

from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.dashboard import DashboardScreen
from screens.send_money import SendMoneyScreen
from screens.transactions import TransactionsScreen
from screens.change_password import ChangePasswordScreen

import db

Window.softinput_mode = "below_target"


class AccessBankApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette  = "Teal"
        self.theme_cls.theme_style     = "Light"
        self.title = "Access Bank"

        # Initialise DB tables on first run
        try:
            db.init_tables()
        except Exception:
            pass

        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(SendMoneyScreen(name="send_money"))
        self.sm.add_widget(TransactionsScreen(name="transactions"))
        self.sm.add_widget(ChangePasswordScreen(name="change_password"))
        return self.sm

    def go_to(self, screen, **kwargs):
        target = self.sm.get_screen(screen)
        for k, v in kwargs.items():
            setattr(target, k, v)
        self.sm.current = screen

    def logout(self):
        self.sm.current = "login"


if __name__ == "__main__":
    AccessBankApp().run()
