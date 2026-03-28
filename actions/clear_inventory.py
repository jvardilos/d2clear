import time
from api import get_current_user, get_characters, get_character_inventory, transfer_to_vault

CLASS_NAMES = {0: "Titan", 1: "Hunter", 2: "Warlock"}


def clear_inventory():
    user = get_current_user()
    memberships = user["destinyMemberships"]

    # Prefer Steam (type 3), fall back to first membership
    membership = next((m for m in memberships if m["membershipType"] == 3), memberships[0])
    membership_type = membership["membershipType"]
    membership_id = membership["membershipId"]

    print(f"Clearing inventory for {membership['displayName']} (membershipType={membership_type})")

    characters = get_characters(membership_type, membership_id)
    for char_id, char_data in characters.items():
        class_name = CLASS_NAMES.get(char_data.get("classType"), "Unknown")
        print(f"\n  [{class_name}] character {char_id}")

        items = get_character_inventory(membership_type, membership_id, char_id)
        if not items:
            print("    Inventory empty.")
            continue

        print(f"    {len(items)} item(s) to transfer...")
        moved, failed = 0, 0
        for item in items:
            item_hash = item["itemHash"]
            item_instance_id = item.get("itemInstanceId", "0")
            quantity = item.get("quantity", 1)
            try:
                transfer_to_vault(item_hash, item_instance_id, quantity, char_id, membership_type)
                moved += 1
            except Exception as e:
                print(f"    ! Failed to move {item_hash} (instanceId={item_instance_id}): {e}")
                failed += 1
            time.sleep(0.1)  # stay within Bungie rate limits

        print(f"    Done: {moved} moved, {failed} failed.")
