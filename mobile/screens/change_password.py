import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import re, random
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


def _generate_otp():
    nums = random.sample(range(1, 11), 6)
    return ''.join(str(n) for n in nums)


class ChangePasswordScreen(Screen):
    user_email = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog  = None
        self._otp     = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Change Password",
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
            text="We'll send a one-time code to your email to verify your identity.",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(50),
        ))

        btn_otp = MDRaisedButton(text="SEND OTP TO EMAIL", size_hint_x=1, height=dp(48))
        btn_otp.bind(on_release=self._send_otp)
        form.add_widget(btn_otp)

        self.otp_field = MDTextField(
            hint_text="Enter OTP code",
            input_filter="int",
            size_hint_y=None,
            height=dp(56),
        )
        self.new_password_field = MDTextField(
            hint_text="New password (8-20 chars)",
            password=True,
            size_hint_y=None,
            height=dp(56),
        )
        self.confirm_field = MDTextField(
            hint_text="Confirm new password",
            password=True,
            size_hint_y=None,
            height=dp(56),
        )

        form.add_widget(self.otp_field)
        form.add_widget(self.new_password_field)
        form.add_widget(self.confirm_field)

        btn_change = MDRaisedButton(text="UPDATE PASSWORD", size_hint_x=1, height=dp(48))
        btn_change.bind(on_release=self._handle_change)
        form.add_widget(btn_change)

        root.add_widget(form)
        self.add_widget(root)

    def _send_otp(self, *args):
        try:
            from email_service import send_otp
            self._otp = _generate_otp()
            send_otp(self.user_email, self._otp)
            self._show_dialog("OTP Sent",
                "A one-time code has been sent to your email.\n"
                "Enter it below along with your new password.")
        except Exception as e:
            self._show_dialog("Error", f"Could not send OTP:\n{e}")

    def _handle_change(self, *args):
        otp      = self.otp_field.text.strip()
        new_pwd  = self.new_password_field.text.strip()
        confirm  = self.confirm_field.text.strip()

        if not otp or not new_pwd or not confirm:
            self._show_dialog("Missing Fields", "Please fill in all fields.")
            return

        if self._otp is None:
            self._show_dialog("No OTP", "Please request an OTP first.")
            return

        if otp != self._otp:
            self._show_dialog("Wrong Code", "The OTP is incorrect. Please try again.")
            return

        if not re.match(r"[a-zA-Z0-9.!£$%^&*()_+|]{8,20}$", new_pwd):
            self._show_dialog("Weak Password",
                "Password must be 8-20 characters.")
            return

        if new_pwd != confirm:
            self._show_dialog("Mismatch", "Passwords do not match.")
            return

        try:
            db.update_password(self.user_email, new_pwd)
            self._otp = None
            self.otp_field.text = ""
            self.new_password_field.text = ""
            self.confirm_field.text = ""
            self._show_dialog("Success", "Your password has been updated successfully.")
        except Exception as e:
            self._show_dialog("Error", f"Could not update password:\n{e}")

    def _show_dialog(self, title, text):
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(title=title, text=text,
                                buttons=[MDFlatButton(text="OK",
                                         on_release=lambda x: self._dialog.dismiss())])
        self._dialog.open()

    def _go_back(self):
        App.get_running_app().go_to("dashboard", user_email=self.user_email)
