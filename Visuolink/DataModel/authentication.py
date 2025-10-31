from Visuolink.DataModel.visuolink_client import VisuoLinkClient
from Visuolink.DataModel.userdetails import store_detail, logout

client = VisuoLinkClient()
API = client.base_url

def get_usernames():
    data = client.get_usernames()
    if data is None:
        return []
    return data

def login(username: str, password: str) -> bool:

    user_id = client.do_login(username, password)
    if user_id is None:
        return False

    user_data = client.get_user_detail(user_id)
    if user_data is None:
        return False

    store_detail(
        user_data["username"],
        user_data["name"],
        user_data["email"],
        user_data["phone"]
    )
    return True

def user_logout():
    logout()


def modify_account(username: str, name: str, email: str, phone: str, password: str, old_username: str):
    updated_details = client.modify_profile(username, name, email, phone, password, old_username)

    if updated_details is None:
        return False
    
    store_detail(
        updated_details["username"],
        updated_details["name"],
        updated_details["email"],
        updated_details["phone"]
    )
    return True

def change_password(username, password, new_password):
    return client.change_password(username, password, new_password)

