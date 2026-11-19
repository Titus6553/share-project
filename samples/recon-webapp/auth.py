"""Sign-in. The real single sign-on is not wired up yet; every request is treated as the shop foreman."""
import os

SSO_CLIENT_ID = os.environ.get("SSO_CLIENT_ID", "")
SSO_CLIENT_SECRET = os.environ.get("SSO_CLIENT_SECRET", "")


def current_user(headers):
    # Placeholder until single sign-on is connected.
    return {"email": "foreman@example.org", "name": "Shop foreman"}
