from kivy.storage.jsonstore import JsonStore

store = JsonStore('data.json')


def store_detail(username, name, email, phone):
    store.put('user', username=username, name=name, email=email, phone=phone, is_logged_in=True)


def store_preferences(hand_tracking: bool, volume_change: bool) -> None:
    store.put('pref', hand_tracking=hand_tracking, volume_change=volume_change)


def get_detail():
    if store.exists('user'):
        data = store.get('user')
        return [data.get('username'), data.get('name'), data.get('email'), data.get('phone')]
    return None


def get_preferences():
    if store.exists('pref'):
        data = store.get('pref')
        return [data.get('hand_tracking'), data.get('volume_change')]
    return None


def init_pref():
    if not store.exists('pref'):
        store.put('pref', hand_tracking=False, volume_change=False)


def is_logged_in():
    if store.exists('user'):
        return store.get('user').get('is_logged_in')
    return False


def logout():
    if store.exists('user'):
        store.delete('user')

