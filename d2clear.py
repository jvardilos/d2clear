import requests
import schedule
import time
import json
import os
from urllib.parse import urlparse, parse_qs


API_KEY = os.getenv("BUNGIE_API_KEY")
CLIENT_ID = os.getenv("BUNGIE_CLIENT_ID")
CLIENT_SECRET = os.getenv("BUNGIE_CLIENT_SECRET")

BASE_URL = "https://www.bungie.net/Platform"
AUTH_URL = "https://www.bungie.net/en/OAuth/Authorize"
TOKEN_URL = f"{BASE_URL}/App/OAuth/token/"
TOKEN_FILE = "tokens.json"

REDIRECT_URI = "https://localhost:8080/callback"

# ── Token storage ──────────────────────────────────────────────────────────────


def save_tokens(tokens: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)


def load_tokens() -> dict | None:
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# ── OAuth flow ─────────────────────────────────────────────────────────────────


def get_access_token() -> str:
    """Return a valid access token, running OAuth if needed."""
    tokens = load_tokens()
    if tokens:
        return tokens["access_token"]

    # 1. Print auth URL for the user to open manually
    auth_url = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code"
    print("\nOpen this URL in your browser:")
    print(auth_url)
    print("\nAfter approving, your browser will show an error page at localhost.")
    print("Copy the full URL from the address bar and paste it below.\n")

    # 2. User pastes the redirect URL — extract the code from it
    redirect_url = input("Paste the full redirect URL here: ").strip()
    params = parse_qs(urlparse(redirect_url).query)
    if "code" not in params:
        raise RuntimeError("No auth code found in URL. Did you paste the full redirect URL?")
    auth_code = params["code"][0]
    print(f"Got auth code: {auth_code[:6]}...")

    # 3. Exchange auth code for tokens
    print("Exchanging code for tokens...")
    response = requests.post(
        TOKEN_URL,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    tokens = response.json()
    save_tokens(tokens)
    print("Tokens saved.")
    return tokens["access_token"]


def authed_headers() -> dict:
    return {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {get_access_token()}",
    }


# ── User lookup ────────────────────────────────────────────────────────────────


def get_current_user() -> dict:
    """
    Returns the authenticated user's Bungie.net profile and all linked
    platform memberships (Steam, Xbox, PSN, etc.).

    Each membership has:
      - membershipType  (3 = Steam, 1 = Xbox, 2 = PSN, 6 = Epic)
      - membershipId    (your Destiny 2 ID on that platform)
      - displayName
    """
    url = f"{BASE_URL}/User/GetMembershipsForCurrentUser/"
    response = requests.get(url, headers=authed_headers())
    response.raise_for_status()
    data = response.json()

    user = data["Response"]
    print(f"Bungie name : {user['bungieNetUser']['uniqueName']}")
    print(f"Memberships :")
    for m in user["destinyMemberships"]:
        print(f"  [{m['membershipType']}] {m['displayName']}  id={m['membershipId']}")

    return user


# ── Inventory clear (stub) ─────────────────────────────────────────────────────


def clear_inventory():
    print("clear_inventory() called at", time.time())
    # TODO: use get_current_user() to get membershipType + membershipId,
    #       then fetch character inventories and transfer items to vault.


if __name__ == "__main__":

    # schedule.every().hour.at("00:00").do(get_fav_weapon)
    schedule.every().minute.at(":00").do(get_current_user)

    while True:
        schedule.run_pending()
