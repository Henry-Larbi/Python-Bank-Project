import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

import db


class DashboardScreen(Screen):
    user_email = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None

    def on_enter(self):
        self.clear_widgets()
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        # Top bar
        toolbar = MDTopAppBar(
            title="Access Bank",
            right_action_items=[["logout", lambda x: self._logout()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # Load account info
        try:
            customer = db.get_customer(self.user_email)
            account  = db.get_account(customer[8]) if customer else None
            name    = customer[0] if customer else "User"
            balance = account[2] if account else 0.0
            acc_id  = account[0] if account else "N/A"
        except Exception:
            name, balance, acc_id = "User", 0.0, "N/A"

        # Greeting
        content.add_widget(MDLabel(
            text=f"Hello, {name.split()[0]}",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40),
        ))

        # Balance card
        balance_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            size_hint_y=None,
            height=dp(120),
            md_bg_color=(0.1, 0.5, 0.1, 1),
            radius=[16],
        )
        balance_card.add_widget(MDLabel(
            text="Account Balance",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(24),
        ))
        balance_card.add_widget(MDLabel(
            text=f"GHS {balance:,.2f}",
            font_style="H4",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50),
        ))
        balance_card.add_widget(MDLabel(
            text=f"Account No: {acc_id}",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.7),
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
        ))
        content.add_widget(balance_card)

        # Quick action buttons
        content.add_widget(MDLabel(
            text="Quick Actions",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30),
        ))

        grid = MDGridLayout(
            cols=2,
            spacing=dp(12),
            size_hint_y=None,
            height=dp(160),
        )

        actions = [
            ("Send Money",    "cash-fast",         "send_money"),
            ("Transactions",  "format-list-bulleted","transactions"),
            ("Change Password","lock-reset",        "change_password"),
            ("Sign Out",      "logout",             None),
        ]

        for label, icon, screen in actions:
            card = MDCard(
                orientation="vertical",
                padding=dp(12),
                size_hint=(1, None),
                height=dp(70),
                radius=[12],
                ripple_behavior=True,
            )
            card.add_widget(MDLabel(
                text=label,
                halign="center",
                font_style="Button",
                theme_text_color="Primary",
            ))
            target_screen = screen

            def make_callback(s):
                def cb(*args):
                    if s is None:
                        self._logout()
                    else:
                        App.get_running_app().go_to(
                            s, user_email=self.user_email)
                return cb

            card.bind(on_release=make_callback(target_screen))
            grid.add_widget(card)

        content.add_widget(grid)
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _logout(self):
        App.get_running_app().logout()

    def _show_dialog(self, title, text):
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(title=title, text=text,
                                buttons=[MDFlatButton(text="OK",
                                         on_release=lambda x: self._dialog.dismiss())])
        self._dialog.open()
