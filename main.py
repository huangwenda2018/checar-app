# -*- coding: utf-8 -*-
"""
搬车APP - 交警挪车短信监听核心 (稳定版)
"""
import time
import threading
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from plyer import notification, vibrator, tts
from android import mActivity
import android

class PlateWidget(BoxLayout):
    def __init__(self, plate='', active=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '48dp'
        self.padding = '10dp'
        self.spacing = '10dp'
        
        self.plate_label = Label(
            text=plate,
            size_hint_x=0.6,
            halign='left',
            color=(0, 0, 0, 1) if active else (0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.plate_label)
        
        self.switch = Switch(active=active, size_hint_x=0.2)
        self.add_widget(self.switch)
        
        self.delete_btn = Button(
            text='❌',
            size_hint_x=0.2,
            background_color=(1, 0.2, 0.2, 1) if active else (0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.delete_btn)

class MainLayout(BoxLayout):
    plates = []
    service_running = False
    config_file = "/sdcard/checar_config.json"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '10dp'
        self.spacing = '10dp'
        
        self.app = App.get_running_app()
        self.load_config()
        self.init_ui()
    
    def init_ui(self):
        # 输入区域
        input_layout = BoxLayout(size_hint_y=None, height='40dp', spacing='5dp')
        self.plate_input = TextInput(
            hint_text='输入车牌号 (如 京A12345)',
            multiline=False,
            size_hint_x=0.7
        )
        input_layout.add_widget(self.plate_input)
        
        add_btn = Button(
            text='添加',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1)
        )
        add_btn.bind(on_release=self.add_plate)
        input_layout.add_widget(add_btn)
        self.add_widget(input_layout)
        
        # 状态区域
        status_layout = BoxLayout(size_hint_y=None, height='40dp', spacing='10dp')
        status_layout.add_widget(Label(text='监听状态:', size_hint_x=0.4))
        
        self.status_label = Label(
            text='● 运行中' if self.service_running else '○ 已停止',
            color=(0, 1, 0, 1) if self.service_running else (0.5, 0.5, 0.5, 1),
            size_hint_x=0.3
        )
        status_layout.add_widget(self.status_label)
        
        self.toggle_btn = Button(
            text='启动' if not self.service_running else '停止',
            size_hint_x=0.3,
            background_color=(0, 1, 0, 1) if not self.service_running else (1, 0, 0, 1)
        )
        self.toggle_btn.bind(on_release=self.toggle_service)
        status_layout.add_widget(self.toggle_btn)
        self.add_widget(status_layout)
        
        # 车牌列表
        scroll = ScrollView()
        self.plates_grid = GridLayout(cols=1, spacing='5dp', size_hint_y=None)
        self.plates_grid.bind(minimum_height=self.plates_grid.setter('height'))
        scroll.add_widget(self.plates_grid)
        self.add_widget(scroll)
        
        # 底部按钮
        bottom_layout = BoxLayout(size_hint_y=None, height='40dp', spacing='10dp')
        
        settings_btn = Button(
            text='⚙️ 设置',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        settings_btn.bind(on_release=self.open_settings)
        bottom_layout.add_widget(settings_btn)
        
        test_btn = Button(
            text='📋 测试提醒',
            background_color=(0.8, 0.5, 0, 1)
        )
        test_btn.bind(on_release=self.test_alert)
        bottom_layout.add_widget(test_btn)
        self.add_widget(bottom_layout)
        
        self.update_plates_display()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.plates = config.get('plates', [])
                    self.app.alert_config.update(config.get('alert_config', {}))
            else:
                self.plates = ["京A12345", "粤B88888"]
                self.save_config()
        except:
            self.plates = ["京A12345", "粤B88888"]
    
    def save_config(self):
        try:
            config = {
                'plates': self.plates,
                'alert_config': self.app.alert_config
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def update_plates_display(self):
        self.plates_grid.clear_widgets()
        for plate in self.plates:
            widget = PlateWidget(plate=plate, active=self.service_running)
            widget.delete_btn.bind(on_release=lambda btn, p=plate: self.remove_plate(p))
            self.plates_grid.add_widget(widget)
    
    def add_plate(self, instance):
        new_plate = self.plate_input.text.strip().upper()
        if new_plate and new_plate not in self.plates:
            self.plates.append(new_plate)
            self.save_config()
            self.update_plates_display()
            self.plate_input.text = ''
    
    def remove_plate(self, plate):
        if plate in self.plates:
            self.plates.remove(plate)
            self.save_config()
            self.update_plates_display()
    
    def toggle_service(self, instance):
        if not self.service_running:
            if self.app.start_monitor(self.plates):
                self.service_running = True
        else:
            self.app.stop_monitor()
            self.service_running = False
        
        self.status_label.text = '● 运行中' if self.service_running else '○ 已停止'
        self.status_label.color = (0, 1, 0, 1) if self.service_running else (0.5, 0.5, 0.5, 1)
        self.toggle_btn.text = '启动' if not self.service_running else '停止'
        self.toggle_btn.background_color = (0, 1, 0, 1) if not self.service_running else (1, 0, 0, 1)
        self.update_plates_display()
    
    def open_settings(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text=f"震动时长: {self.app.alert_config['vibrate_time']/1000}秒"))
        vibrate_slider = Slider(min=1, max=10, value=self.app.alert_config['vibrate_time']/1000)
        content.add_widget(vibrate_slider)
        
        content.add_widget(Label(text=f"播报次数: {self.app.alert_config['play_times']}"))
        play_slider = Slider(min=1, max=10, value=self.app.alert_config['play_times'], step=1)
        content.add_widget(play_slider)
        
        def save_settings(btn):
            self.app.alert_config['vibrate_time'] = int(vibrate_slider.value * 1000)
            self.app.alert_config['play_times'] = int(play_slider.value)
            self.save_config()
            popup.dismiss()
        
        content.add_widget(Button(text='保存', on_release=save_settings))
        
        popup = Popup(title='设置', content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def test_alert(self, instance):
        if self.plates:
            self.app.test_alert(self.plates[0])

class CheCarApp(App):
    def __init__(self):
        super().__init__()
        self.monitor_running = False
        self.plate_list = []
        self.alert_config = {
            "vibrate_time": 3000,
            "play_times": 3,
            "voice_text": "你的车违停了，请立即挪车！"
        }
        self.monitor_thread = None
        self.last_alert_time = {}
        self.ALERT_INTERVAL = 300
    
    def build(self):
        self.title = '搬车APP'
        return MainLayout()
    
    def load_plates(self):
        """兼容旧代码"""
        pass
    
    def start_monitor(self, plates):
        self.plate_list = plates
        if not self.plate_list:
            return False
        
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_sms, daemon=True)
        self.monitor_thread.start()
        return True
    
    def stop_monitor(self):
        self.monitor_running = False
    
    def _monitor_sms(self):
        police_keywords = [
            "交警", "交管12123", "未按规定停放", "立即驶离",
            "依法予以处罚", "违停", "抄牌", "挪车", "违法停车"
        ]
        
        while self.monitor_running and self.plate_list:
            try:
                # 使用 android 模块读取短信
                sms_uri = android.Android().getContentResolver().call(
                    "content://sms/inbox", "query", None, None
                )
                # 简化处理，实际需要正确实现
                
                time.sleep(3)
            except Exception as e:
                print(f"监听异常：{e}")
                time.sleep(3)
    
    def test_alert(self, plate):
        try:
            vibrator.vibrate(self.alert_config["vibrate_time"] / 1000)
            notification.notify(
                title="🚨 测试提醒",
                message=f"这是测试提醒，监控车牌 {plate}",
                app_name="搬车APP",
                timeout=5
            )
            tts.speak("这是测试提醒")
        except:
            pass

if __name__ == "__main__":
    CheCarApp().run()
