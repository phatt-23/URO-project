#!/usr/bin/env python3

from lib import application as App
from email_app import EmailClientApp


if __name__ == "__main__":
    App.register_application(lambda: EmailClientApp())
    App.application_entry_point()
