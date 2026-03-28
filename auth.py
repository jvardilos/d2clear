import os
import json
import time
import requests
from urllib.parse import urlparse, parse_qs

API_KEY = os.getenv("BUNGIE_API_KEY")
CLIENT_ID = os.getenv("BUNGIE_CLIENT_ID")
CLIENT_SECRET = os.getenv("BUNGIE_CLIENT_SECRET")

BASE_URL = "https://www.bungie.net/Platform"
AUTH_URL = "https://www.bungie.net/en/OAuth/Authorize"
TOKEN_URL = f"{BASE_URL}/App/OAuth/token/"
TOKEN_FILE = "tokens.json"
REDIRECT_URI = "https://localhost:8080/callback"


def save_tokens(tokens: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def load_tokens() -> dict | None:
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _exchange_code(auth_code: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens["obtained_at"] = time.time()
    save_tokens(tokens)
    return tokens


def _refresh_tokens(refresh_token: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens["obtained_at"] = time.time()
    save_tokens(tokens)
    return tokens


def get_access_token() -> str:
    """Return a valid access token, refreshing or running the full OAuth flow as needed."""
    tokens = load_tokens()

    if tokens:
        obtained_at = tokens.get("obtained_at", 0)
        expires_in = tokens.get("expires_in", 3600)
        still_valid = time.time() < obtained_at + expires_in - 60

        if still_valid:
            return tokens["access_token"]

        if "refresh_token" in tokens:
            print("Access token expired — refreshing...")
            return _refresh_tokens(tokens["refresh_token"])["access_token"]

    # Full interactive OAuth flow
    auth_url = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code"
    print("\nOpen this URL in your browser:")
    print(auth_url)
    print("\nAfter approving, your browser will redirect to localhost (it will error — that's fine).")
    print("Copy the full URL from the address bar and paste it below.\n")

    redirect_url = input("Paste the full redirect URL here: ").strip()
    params = parse_qs(urlparse(redirect_url).query)
    if "code" not in params:
        raise RuntimeError("No auth code found in URL. Did you paste the full redirect URL?")

    auth_code = params["code"][0]
    print("Exchanging code for tokens...")
    tokens = _exchange_code(auth_code)
    print("Tokens saved.")
    return tokens["access_token"]


def authed_headers() -> dict:
    return {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {get_access_token()}",
    }
