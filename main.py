from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from PIL import Image as PILImage
import requests
from io import BytesIO
import random
import json
import os

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.image = self.ids.image
        self.is_loading_image = False

    def fetch_image(self, instance):
        if self.is_loading_image: return
        self.is_loading_image = True

        if not App.get_running_app().tags:
            print("No tags available. Please add some tags first.")
            self.is_loading_image = False
            return

        topic = random.choice(App.get_running_app().tags)
        url = f"https://api.rule34.xxx/index.php?page=dapi&json=1&s=post&q=index&tags={topic}"

        response = requests.get(url)
        data = response.json()
        if data and isinstance(data, list):
            if data:
                image_url = random.choice(data)['file_url']
                self.display_image(image_url)
            else:
                self.image.source = ''
                self.is_loading_image = False
        else:
            self.image.source = ''
            self.is_loading_image = False

    def display_image(self, image_url):
        try:
            image_data = requests.get(image_url).content
            pil_image = PILImage.open(BytesIO(image_data))
            pil_image = pil_image.convert('RGBA')

            kivy_image = CoreImage(BytesIO(image_data), ext='png')
            self.image.texture = kivy_image.texture
            self.image.allow_stretch = True
            self.image.keep_ratio = True
            self.is_loading_image = False
        except Exception as e:
            print(f"Error loading image: {e}")
            self.is_loading_image = False

    def save_image(self, instance):
        if self.image.texture:
            try:
                texture = self.image.texture
                pixels = texture.pixels
                width = int(texture.width)
                height = int(texture.height)
                pil_image = PILImage.frombytes('RGBA', (width, height), pixels)
                random_number = random.randint(1, 10000)
                pil_image.save(f'saved_image_{random_number}.png')
            except Exception as e:
                print(f"Error saving image: {e}")

    def go_to_tag_manager(self, instance):
        self.manager.current = 'tag_manager'

class TagManagerScreen(Screen):
    def __init__(self, **kwargs):
        super(TagManagerScreen, self).__init__(**kwargs)
        self.tag_input = self.ids.tag_input
        self.tags_layout = self.ids.tags_layout

    def add_tag(self, instance):
        tag = self.tag_input.text.strip()
        if tag and tag not in App.get_running_app().tags:
            App.get_running_app().tags.append(tag)
            App.get_running_app().save_tags()
            self.update_tags_display()
            self.tag_input.text = ''

    def delete_tag(self, tag):
        if tag in App.get_running_app().tags:
            App.get_running_app().tags.remove(tag)
            App.get_running_app().save_tags()
            self.update_tags_display()

    def update_tags_display(self):
        self.tags_layout.clear_widgets()
        for tag in App.get_running_app().tags:
            tag_layout = BoxLayout(size_hint_y=None, height=40)
            tag_label = Button(text=tag, size_hint=(0.7, None), height=40, background_color=(1, 1, 1, 1))
            delete_button = Button(text='Remove', size_hint=(0.3, None), height=40)
            delete_button.bind(on_press=lambda btn, t=tag: self.delete_tag(t))
            tag_layout.add_widget(tag_label)
            tag_layout.add_widget(delete_button)
            self.tags_layout.add_widget(tag_layout)

    def go_to_main(self, instance):
        self.manager.current = 'main'

class NSFWApp(App):
    tags_file = 'tags.json'
    
    def build(self):
        Builder.load_file('myapp.kv')
        self.load_tags()
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(TagManagerScreen(name='tag_manager'))
        
        return sm

    def load_tags(self):
        if os.path.exists(self.tags_file):
            with open(self.tags_file, 'r') as f:
                self.tags = json.load(f)
        else:
            self.tags = []

    def save_tags(self):
        with open(self.tags_file, 'w') as f:
            json.dump(self.tags, f)

if __name__ == '__main__':
    NSFWApp().run()
