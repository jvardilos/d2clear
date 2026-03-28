import requests
from auth import BASE_URL, authed_headers


def get_current_user() -> dict:
    """Returns the authenticated user's Bungie profile and linked platform memberships."""
    resp = requests.get(f"{BASE_URL}/User/GetMembershipsForCurrentUser/", headers=authed_headers())
    resp.raise_for_status()
    return resp.json()["Response"]


def get_characters(membership_type: int, membership_id: str) -> dict:
    """Returns a dict of characterId -> character data for the given membership."""
    url = f"{BASE_URL}/Destiny2/{membership_type}/Profile/{membership_id}/?components=200"
    resp = requests.get(url, headers=authed_headers())
    resp.raise_for_status()
    return resp.json()["Response"]["characters"]["data"]


def get_character_inventory(membership_type: int, membership_id: str, character_id: str) -> list:
    """Returns the non-equipped item list for a character's inventory."""
    url = f"{BASE_URL}/Destiny2/{membership_type}/Profile/{membership_id}/Character/{character_id}/?components=201"
    resp = requests.get(url, headers=authed_headers())
    resp.raise_for_status()
    return resp.json()["Response"]["inventory"]["data"]["items"]


def transfer_to_vault(
    item_reference_hash: int,
    item_instance_id: str,
    stack_size: int,
    character_id: str,
    membership_type: int,
) -> dict:
    """Transfer a single item from a character's inventory to the vault."""
    resp = requests.post(
        f"{BASE_URL}/Destiny2/Actions/Items/TransferItem/",
        headers=authed_headers(),
        json={
            "itemReferenceHash": item_reference_hash,
            "stackSize": stack_size,
            "transferToVault": True,
            "itemId": item_instance_id,
            "characterId": character_id,
            "membershipType": membership_type,
        },
    )
    resp.raise_for_status()
    return resp.json()
