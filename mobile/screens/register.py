import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import re, random, string
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

import db


def _generate_account_id():
    return int(''.join(random.sample('123456789', 9)) + str(random.randint(100000, 999999)))


def _generate_bank_username(name):
    parts = name.strip().split()
    base = ''.join(p[:3].lower() for p in parts[:2])
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{base}{suffix}"


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        scroll = ScrollView()
        root = MDBoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(12),
            size_hint_y=None,
        )
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(MDLabel(
            text="Create Account",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(60),
        ))

        def field(hint, **kwargs):
            f = MDTextField(hint_text=hint, size_hint_y=None, height=dp(56), **kwargs)
            root.add_widget(f)
            return f

        self.name_field     = field("Full Name  (e.g. John Henry Doe)")
        self.age_field      = field("Age", input_filter="int")
        self.location_field = field("Location (letters only)")
        self.phone_field    = field("Phone  (050-000-0000)")
        self.email_field    = field("Email address")
        self.password_field = field("Password (8-20 chars)", password=True)
        self.confirm_field  = field("Confirm Password", password=True)

        # Generate password button
        gen_btn = MDFlatButton(text="Generate strong password", size_hint_x=1)
        gen_btn.bind(on_release=self._generate_password)
        root.add_widget(gen_btn)

        btn_reg = MDRaisedButton(text="CREATE ACCOUNT", size_hint_x=1, height=dp(48))
        btn_reg.bind(on_release=self._handle_register)
        root.add_widget(btn_reg)

        btn_back = MDFlatButton(text="Already have an account? Sign In", size_hint_x=1)
        btn_back.bind(on_release=lambda x: setattr(
            App.get_running_app().sm, 'current', 'login'))
        root.add_widget(btn_back)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def _generate_password(self, *args):
        chars = string.ascii_letters + string.digits + "!$%^&*_+"
        pwd = ''.join(random.choices(chars, k=12))
        self.password_field.text = pwd
        self.confirm_field.text  = pwd

    def _show_dialog(self, title, text):
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(title=title, text=text,
                                buttons=[MDFlatButton(text="OK",
                                         on_release=lambda x: self._dialog.dismiss())])
        self._dialog.open()

    def _handle_register(self, *args):
        name     = self.name_field.text.strip()
        age      = self.age_field.text.strip()
        location = self.location_field.text.strip()
        phone    = self.phone_field.text.strip()
        email    = self.email_field.text.strip()
        password = self.password_field.text.strip()
        confirm  = self.confirm_field.text.strip()

        if not all([name, age, location, phone, email, password, confirm]):
            self._show_dialog("Missing Fields", "Please fill in all fields.")
            return

        name_re = re.compile(r"^[a-zA-Z]{3,8}$")
        for part in name.split():
            if not name_re.match(part):
                self._show_dialog("Invalid Name",
                    "Each word in your name must be 3-8 letters only.")
                return

        try:
            age_int = int(age)
            if not (1 <= age_int <= 119):
                raise ValueError
        except ValueError:
            self._show_dialog("Invalid Age", "Please enter a valid age (1-119).")
            return

        if not re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
            self._show_dialog("Invalid Phone", "Phone must follow format: 050-000-0000")
            return

        if not location.isalpha():
            self._show_dialog("Invalid Location", "Location must contain letters only.")
            return

        if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", email):
            self._show_dialog("Invalid Email", "Please enter a valid email address.")
            return

        if not re.match(r"[a-zA-Z0-9.!£$%^&*()_+|]{8,20}$", password):
            self._show_dialog("Weak Password",
                "Password must be 8-20 characters with letters, digits or special characters.")
            return

        if password != confirm:
            self._show_dialog("Password Mismatch", "Passwords do not match.")
            return

        try:
            if db.is_duplicate(email):
                self._show_dialog("Account Exists",
                    "An account with this email already exists. Please sign in.")
                return

            account_id    = _generate_account_id()
            bank_username = _generate_bank_username(name)
            gender        = "Other"
            status        = "Active"

            db.register(name, age_int, gender, status, location, phone,
                        email, password, account_id)

            self._show_dialog("Account Created!",
                f"Welcome to Access Bank!\n\n"
                f"Bank Username  : {bank_username}\n"
                f"Account Number : {account_id}\n\n"
                f"Please save these details. You can now sign in.")

            for f in [self.name_field, self.age_field, self.location_field,
                      self.phone_field, self.email_field,
                      self.password_field, self.confirm_field]:
                f.text = ""

        except Exception as e:
            self._show_dialog("Registration Error", f"Could not create account:\n{e}")
