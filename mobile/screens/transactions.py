import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

import db


class TransactionsScreen(Screen):
    user_email = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None

    def on_enter(self):
        self.clear_widgets()
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Transactions",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(4),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        try:
            customer = db.get_customer(self.user_email)
            account  = db.get_account(customer[8]) if customer else None
            acc_id   = account[0] if account else None
            txns     = db.get_transactions(acc_id) if acc_id else []
        except Exception as e:
            txns = []
            content.add_widget(MDLabel(
                text=f"Could not load transactions:\n{e}",
                halign="center",
                theme_text_color="Error",
                size_hint_y=None,
                height=dp(60),
            ))

        if not txns:
            content.add_widget(MDLabel(
                text="No transactions yet.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60),
            ))
        else:
            for txn in txns:
                txn_id, from_acc, to_acc, amount, date, status = txn
                if str(from_acc) == str(acc_id):
                    direction = f"Sent to {to_acc}"
                    color = (0.8, 0.1, 0.1, 1)
                    sign = "-"
                else:
                    direction = f"Received from {from_acc}"
                    color = (0.1, 0.6, 0.1, 1)
                    sign = "+"

                item = TwoLineListItem(
                    text=f"{sign}GHS {float(amount):,.2f}  •  {status}",
                    secondary_text=f"{direction}  |  {date}",
                )
                content.add_widget(item)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _go_back(self):
        App.get_running_app().go_to("dashboard", user_email=self.user_email)
