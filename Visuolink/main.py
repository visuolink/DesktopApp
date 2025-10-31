from kivy.uix.accordion import StringProperty
from kivy.config import Config
from platform import system
from Visuolink.Backend.utils import resource_path

Config.set('graphics', 'resizable', False)

if system == "Windows":
    Config.set('kivy', 'window_icon', resource_path('/assets/visuolink.ico'))
elif system in ["Darwin", "Linux"]:
    Config.set('kivy', 'window_icon', resource_path('/assets/visuolink.png'))

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, StringProperty


from Visuolink.DataModel.visuolink_client import start_api_monitor
from Visuolink.DataModel.userdetails import init_pref, get_detail, get_preferences, store_preferences, is_logged_in
from Visuolink.DataModel.authentication import login, user_logout, change_password, modify_account, get_usernames, API
from Visuolink.Backend.launcher.desktop import start_background_hand_tracking, stop_background_hand_tracking

Window.title = "VisuoLink"

start_api_monitor(API)

USER_DATA = None

def set_user_data():
    global USER_DATA
    USER_DATA = get_detail()


def pop_window(title, data, max_width=400, max_height=300):
    content_label = Label(
        text=data,
        font_size=18,
        padding =(15, 10),
        size_hint_y=None,
        text_size=(max_width, None),
        halign="left",
        valign="top"
    )
    
    content_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))

    scroll = ScrollView(size_hint=(1, 1))
    scroll.add_widget(content_label)

    layout = BoxLayout()
    layout.add_widget(scroll)

    popup = Popup(
        title=title,
        content=layout,
        size_hint=(None, None)
    )

    popup.width = min(max_width + 20, 0.8 * popup.get_parent_window().width if popup.get_parent_window() else max_width + 20)
    popup.height = min(content_label.height + 20, max_height)

    popup.open()

class HomeScreen(Screen):
    hand_gesture_image = StringProperty(resource_path('Visuolink/assets/gesture_control.png'))
    volume_gesture_image = StringProperty(resource_path('Visuolink/assets/volume_gesture.png'))
    howtouse_image = StringProperty(resource_path('Visuolink/assets/howtouse.png'))
    mobile_version_image = StringProperty(resource_path('Visuolink/assets/androidversion.png'))
    def on_enter(self, *args):
        self.models_status = get_preferences()
        return super().on_enter(*args)
    
    def run_scripts(self, instance):
        if not is_logged_in():
            pop_window("Invalid Access", "Please Login First!")
            return;

        if not any(self.models_status):
            pop_window("Invalid Model Status", "Enable Models From the setting, please!")
            return;

        if instance.text == "Start":
            instance.text = "Stop"
            start_background_hand_tracking(self.models_status[0], self.models_status[1])
        else:
            stop_background_hand_tracking()
            instance.text = "Start"


class SettingScreen(Screen):
    def on_enter(self, *args):
        self.set_pref()
        return super().on_enter(*args)

    def apply_changes(self, instance):
        hand_tracking = self.ids.hand_tracking.active
        volume_control = self.ids.volume_control.active
        store_preferences(hand_tracking, volume_control)
        pop_window("Apply Changes", "Changes are applied!")

    def manage_account(self, instance):
        if not is_logged_in():
            pop_window("Invalid Access", "please login to manage account!")
            return;
        self.manager.current = 'manage_account'

    def change_password(self, instance):
        if not is_logged_in():
            pop_window("Invalid Access", "Unauthorized Access")
            return;
        self.manager.current = 'change_password'

    def set_pref(self):
        pref = get_preferences()
        self.ids.hand_tracking.active = pref[0]
        self.ids.volume_control.active = pref[1]


class ManageAccountScreen(Screen):
    person_image = StringProperty(resource_path('Visuolink/assets/person.png'))
    def on_enter(self, *args):
        self.input_fields = [self.ids.username, self.ids.name, self.ids.email, self.ids.phone, self.ids.password]
        self.set_info()
        self.usernames = get_usernames()
        self.submit_btn = self.ids.manage_account_btn
        return super().on_enter(*args)
    
    def set_info(self):
        if USER_DATA is not None:
            self.input_fields[0].text = USER_DATA[0]
            self.input_fields[1].text = USER_DATA[1]
            self.input_fields[2].text = USER_DATA[2]
            self.input_fields[3].text = USER_DATA[3]
    
    def submit(self, instance):
        mode = self.submit_btn.text
        data = [self.input_fields[0].text, self.input_fields[1].text, self.input_fields[2].text, 
                self.input_fields[3].text, self.input_fields[4].text]

        if mode.lower() != "submit":
            self.submit_btn.text = "Submit"
            for field in self.input_fields:
                field.readonly = False
                field.background_color = 0.1, 0.1, 0.1, 1
        else:
            if USER_DATA[0] != data[0]:
                if data[0] in self.usernames:
                    pop_window("Unique Invalid", "username already exist!")
                    return
                
            success = modify_account(username=data[0], name=data[1], email=data[2], phone=data[3], password=data[4], old_username=USER_DATA[0])
            
            if not success:
                pop_window("API Error", "Unique constaint invalid!")
                return
            
            set_user_data()

            for field in self.input_fields:
                field.readonly = True
                field.background_color= 0.02, 0.02, 0.02, 1
            data[4] = ""
            self.submit_btn.text = "Edit"

            pop_window("Status", "Information updated!")


class ChangePasswordScreen(Screen):
    person_image = StringProperty(resource_path("Visuolink/assets/visuolink.png"))
    def on_enter(self, *args):
        self.submit_btn = self.ids.change_password_btn
        self.input_fields = [self.ids.old_password, self.ids.new_password, self.ids.confirm_password]
        return super().on_enter(*args)
    
    def submit(self, instance):
        mode = self.submit_btn.text
        if mode.lower() != "submit":
            self.submit_btn.text = "Submit"
            for field in self.input_fields:
                field.readonly = False
                field.background_color = 0.1, 0.1, 0.1, 1
        else:
            if self.input_fields[1] == self.input_fields[2]:
                pop_window("Password Mismatch", "New password and confirm password must match!")
                return

            success = change_password(USER_DATA[0], self.input_fields[0].text, self.input_fields[2].text)
            if not success:
                pop_window("API Error", "Password does not change!")
                return
            
            self.submit_btn.text = "Edit"
            for field in self.input_fields:
                field.text = ""
                field.readonly = True
                field.background_color= 0.02, 0.02, 0.02, 1
            
            pop_window("Status", "Password changed successfully!")

class LoginScreen(Screen):
    person_image = StringProperty(resource_path('Visuolink/assets/person.png'))
    def login(self, instance):
        username = self.ids.username
        password = self.ids.password
        success = login(username.text, password.text)
        if not success:
            pop_window("API Error", "Credential Invalid or API Down!")
            return
        if is_logged_in():
            username.text = ""
            password.text = ""
            self.manager.current = 'profile'

class ProfileScreen(Screen):
    person_image = StringProperty(resource_path('Visuolink/assets/person.png'))
    def on_enter(self, *args):
        set_user_data()
        if USER_DATA is not None:
            self.ids.username_label.text = USER_DATA[0]
            self.ids.name_label.text = USER_DATA[1]
            self.ids.email_label.text = f'Email: {USER_DATA[2]}'
            self.ids.phone_label.text = f'Phone: {USER_DATA[3]}'
        return super().on_enter(*args)

    def logout(self, instance):
        user_logout()
        self.manager.current = 'login'


class VisuoLink(App):
    current_screen_name = ObjectProperty("Home")
    def build(self):
        init_pref()
        set_user_data()
        self.create_toolbar_dropdown()
        return super().build()


    def create_toolbar_dropdown(self):
        self.dropdown = DropDown()
        for item in ["Update", "About", "Policy"]:
            btn = Button(text=item, size_hint_y=None, height=40, background_color=(0.1, 0.1, 0.1, 1))
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

        menu_btn = self.root.ids.menu_button
        menu_btn.bind(on_release=self.dropdown.open)

        self.dropdown.bind(on_select=self.menu_item_selected)

    def menu_item_selected(self, dropdown, selection):
        data = ""
        if selection == "Update":
            data += "Up to date \n no new version available"
        elif selection == "About":
            data += (
                "Made using: Python\n"
                "Frontend: Kivy\n"
                "Backend: Mediapipe(Gesture), FastAI(Data)\n"
                "Developer: Sumit Dubey\n"
                "Current Version: V1.07"
            )
        elif selection == "Policy":
            data += (
                "Our app only uses the credentials you provide to allow access to your account. "
                "We do not store or transmit any other personal data. "
                "Your credentials are kept secure and used solely for authentication purposes."
            )

        content_label = Label(
            text=data,
            padding=(10, 10),
            font_size=18,
            size_hint_y=None,
            text_size=(350, None),
            halign="left",
            valign="top"
        )
        content_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(content_label)

        popup = Popup(title=selection, content=scroll_view, size_hint=(0.4, 0.3))
        popup.open()


    def change_screen(self, screen_name):
        screen_manager = self.root.ids.screen_manager
        current = screen_manager.current
        navigation_button = [
            self.root.ids.home_button,
            self.root.ids.setting_button,
            self.root.ids.profile_button,
        ]

        for navigation in navigation_button:
            if navigation.text.lower() == screen_name:
                navigation.background_color = (0.2, 0.2, 0.2, 1)
            else:
                navigation.background_color = (0.4, 0.4, 0.4, 1)

        if screen_name == "profile":
            screen_name = "profile" if is_logged_in() else "login"

        screen_order = ["home", "settings", "profile", "login"]

        try:
            current_index = screen_order.index(current)
            new_index = screen_order.index(screen_name)
        except ValueError:
            screen_manager.transition.direction = "left"
        else:
            if new_index > current_index:
                screen_manager.transition.direction = "left"
            else:
                screen_manager.transition.direction = "right"

        screen_manager.current = screen_name
        self.current_screen_name = screen_name.capitalize()


if __name__ == '__main__':
    VisuoLink().run()
