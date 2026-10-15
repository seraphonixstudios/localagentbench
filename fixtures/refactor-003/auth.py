"""User auth with DUPLICATED validation. Task: extract shared validators."""
from __future__ import annotations


def register(email, password, users):
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("invalid email")
    if len(password) < 8 or not any(c.isdigit() for c in password):
        raise ValueError("weak password")
    if email in users:
        raise ValueError("already registered")
    users[email] = password
    return True


def change_password(email, old_password, new_password, users):
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("invalid email")
    if users.get(email) != old_password:
        raise ValueError("wrong password")
    if len(new_password) < 8 or not any(c.isdigit() for c in new_password):
        raise ValueError("weak password")
    users[email] = new_password
    return True
