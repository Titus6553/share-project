"""Texts the assigned tech when a car moves to their stage. Stubbed: prints instead of sending."""
import json

with open("config.json") as f:
    _cfg = json.load(f)


def text_tech(phone, message):
    # Real call would POST to _cfg["notify_url"] with _cfg["notify_token"].
    print(f"[notify stub] to {phone}: {message}")
