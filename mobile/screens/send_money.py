import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import random
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp

import db


def _generate_txn_id():
    nums = random.sample(range(1, 10), 9)
    return int(''.join(str(n) for n in nums))


class SendMoneyScreen(Screen):
    user_email = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Send Money",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        form = MDBoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(16),
        )

        form.add_widget(MDLabel(
            text="Transfer funds to another account",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30),
        ))

        self.recipient_field = MDTextField(
            hint_text="Recipient account number (15 digits)",
            input_filter="int",
            size_hint_y=None,
            height=dp(56),
        )
        self.amount_field = MDTextField(
            hint_text="Amount (GHS)",
            input_filter="float",
            size_hint_y=None,
            height=dp(56),
        )

        form.add_widget(self.recipient_field)
        form.add_widget(self.amount_field)

        btn = MDRaisedButton(text="SEND MONEY", size_hint_x=1, height=dp(48))
        btn.bind(on_release=self._handle_send)
        form.add_widget(btn)

        root.add_widget(form)
        self.add_widget(root)

    def _go_back(self):
        App.get_running_app().go_to("dashboard", user_email=self.user_email)

    def _show_dialog(self, title, text):
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(title=title, text=text,
                                buttons=[MDFlatButton(text="OK",
                                         on_release=lambda x: self._dialog.dismiss())])
        self._dialog.open()

    def _handle_send(self, *args):
        recipient = self.recipient_field.text.strip()
        amount_str = self.amount_field.text.strip()

        if not recipient or not amount_str:
            self._show_dialog("Missing Fields", "Please fill in all fields.")
            return

        if not (recipient.isdigit() and len(recipient) == 15):
            self._show_dialog("Invalid Account",
                "Recipient account number must be exactly 15 digits.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self._show_dialog("Invalid Amount", "Please enter a valid amount greater than 0.")
            return

        try:
            customer   = db.get_customer(self.user_email)
            account    = db.get_account(customer[8])
            sender_id  = account[0]

            if str(sender_id) == recipient:
                self._show_dialog("Invalid Transfer", "You cannot send money to yourself.")
                return

            new_balance, error = db.transfer(sender_id, recipient, amount)
            if error:
                self._show_dialog("Transfer Failed", error)
                return

            txn_id = _generate_txn_id()
            db.record_transaction(txn_id, sender_id, recipient, amount)

            self.recipient_field.text = ""
            self.amount_field.text    = ""

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._show_dialog("Transfer Successful",
                f"GHS {amount:.2f} sent to account {recipient}\n\n"
                f"Transaction ID  : {txn_id}\n"
                f"Date & Time     : {now}\n"
                f"Remaining Balance: GHS {new_balance:.2f}")

        except Exception as e:
            self._show_dialog("Error", f"Transfer could not be completed:\n{e}")
