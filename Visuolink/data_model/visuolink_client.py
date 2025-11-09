from typing import Optional, List, Dict, Any
import requests
import threading
from time import sleep


class VisuoLinkClient:
    def __init__(self, base_url: str = "https://visuolinkapi.onrender.com", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"[Error] Request to {url} failed: {e}")
            return None

    def get_usernames(self) -> Optional[List[str]]:
        response = self._request("GET", "/users")
        if response:
            return [user.get("username") for user in response.json()]
        return None
    
    def get_user_detail(self, user_id: int) -> Optional[Dict[str, Any]]:
        response = self._request("GET", f"/users/{user_id}")
        if response:
            data = response.json()
            return {
                "username": data.get("username"),
                "name": data.get("name"),
                "email": data.get("email"),
                "phone": data.get("phone")
            }
        return None

    def do_login(self, username: str, password: str) -> Optional[int]:
        payload = {"username": username, "password": password}
        response = self._request("POST", "/users/auth/login", json=payload)
        if response:
            return response.json().get("id")
        return None

    def change_password(self, username: str, password: str, new_password: str) -> bool:
        payload = {"username": username, "password": password, "newPassword": new_password}
        response = self._request("PUT", "/users/cp", json=payload)
        return response is not None and response.status_code == 202

    def modify_profile(
        self, username: str, name: str, email: str, phone: str,
        password: str, old_username: str
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "username": username,
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "oldUsername": old_username
        }
        response = self._request("PUT", "/users", json=payload)
        if response and response.status_code == 202:
            data = response.json()
            return {
                "username": data.get("username"),
                "name": data.get("name"),
                "email": data.get("email"),
                "phone": data.get("phone")
            }
        return None



API_UP = False
def check_api_in_background(url: str, interval: int = 8, max_retries: int = 8):
    global API_UP

    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                API_UP = True
                return
            else:
                print(f"⚠️ API responded with {response.status_code}")
        except Exception as e:
            print(f"❌ API Error ({i+1}/{max_retries}): {e}")
        sleep(interval)
    print(f"❌ Could not connect to API after {max_retries} attempts.")

def start_api_monitor(url: str):
    thread = threading.Thread(target=check_api_in_background, args=(url,), daemon=True)
    thread.start()
    return thread

