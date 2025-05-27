# password_checker.py

import re

def check_password_strength(password):
    length_error = len(password) < 8
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(r"[!@#$%^&*(),.?\":{}|<>]", password) is None

    errors = [length_error, digit_error, uppercase_error, lowercase_error, symbol_error]
    error_count = sum(errors)

    if error_count == 0:
        return "Strong", "✅ This password is strong."
    elif error_count <= 2:
        return "Moderate", "⚠️ Your password could be improved."
    else:
        return "Weak", "❌ Your password is weak. Try using uppercase, numbers, and symbols."
