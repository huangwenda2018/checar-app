# -*- coding: utf-8 -*-
"""
搬车APP - 交警挪车短信监听核心 + Kivy UI
参考挪呗UI风格，简洁易用
"""
import time
import threading
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty, DictProperty
from androidhelper import Android
from plyer import notification, vibrator, tts

droid = Android()

class MainLayout(BoxLayout):
    """主界面布局"""
    plates = ListProperty([])  # 存储车牌列表
    service_running = BooleanProperty(False)  # 监听服务状态
    config_file = "/sdcard/checar_config.json"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.load_config()
        self.update_plates_display()
    
    def load_config(self):
        """加载配置（车牌、设置）"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.plates = config.get('plates', [])
                    self.app.alert_config.update(config.get('alert_config', {}))
            else:
                # 默认测试车牌
                self.plates = ["京A12345", "粤B88888"]
                self.save_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.plates = ["京A12345", "粤B88888"]
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'plates': self.plates,
                'alert_config': self.app.alert_config
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def update_plates_display(self):
        """更新界面显示的车牌列表"""
        grid = self.ids.plates_grid
        grid.clear_widgets()
        for plate in self.plates:
            # 从KV文件动态创建PlateWidget
            from kivy.lang import Builder
            widget = Builder.load_string(f'''
PlateWidget:
    plate: '{plate}'
    active: {str(self.app.monitor_running).lower()}
''')
            grid.add_widget(widget)
    
    def add_plate(self):
        """添加新车牌"""
        input_field = self.ids.new_plate_input
        new_plate = input_field.text.strip().upper()
        if new_plate and new_plate not in self.plates:
            self.plates.append(new_plate)
            self.save_config()
            self.update_plates_display()
            input_field.text = ''
    
    def remove_plate(self, plate):
        """删除车牌"""
        if plate in self.plates:
            self.plates.remove(plate)
            self.save_config()
            self.update_plates_display()
    
    def toggle_monitor(self, plate, active):
        """切换对某个车牌的监控（预留）"""
        # 可以在服务运行状态下单独控制每个车牌
        pass
    
    def toggle_service(self):
        """启动/停止监听服务"""
        if not self.service_running:
            # 启动服务
            if self.app.start_monitor(self.plates):
                self.service_running = True
                self.update_plates_display()
        else:
            # 停止服务
            self.app.stop_monitor()
            self.service_running = False
            self.update_plates_display()
    
    def open_settings(self):
        """打开设置界面（简化版）"""
        # 这里可以弹出一个Popup修改震动时长、播报次数等
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.slider import Slider
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"震动时长: {self.app.alert_config['vibrate_time']/1000}秒"))
        vibrate_slider = Slider(min=1, max=10, value=self.app.alert_config['vibrate_time']/1000)
        content.add_widget(vibrate_slider)
        
        content.add_widget(Label(text=f"播报次数: {self.app.alert_config['play_times']}"))
        play_slider = Slider(min=1, max=10, value=self.app.alert_config['play_times'], step=1)
        content.add_widget(play_slider)
        
        def save_settings(instance):
            self.app.alert_config['vibrate_time'] = int(vibrate_slider.value * 1000)
            self.app.alert_config['play_times'] = int(play_slider.value)
            self.save_config()
            popup.dismiss()
        
        content.add_widget(Button(text='保存', on_release=save_settings))
        
        popup = Popup(title='设置', content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def test_alert(self):
        """测试提醒功能"""
        if self.plates:
            self.app.test_alert(self.plates[0])


class CheCarApp(App):
    """主应用类"""
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
        self.ALERT_INTERVAL = 300  # 5分钟
    
    def build(self):
        self.title = '搬车APP'
        return MainLayout()
    
    def start_monitor(self, plates):
        """启动监听"""
        self.plate_list = plates
        if not self.plate_list:
            return False
        
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_sms, daemon=True)
        self.monitor_thread.start()
        print(f"监听服务已启动，监控车牌：{self.plate_list}")
        return True
    
    def stop_monitor(self):
        """停止监听"""
        self.monitor_running = False
        print("监听服务已停止")
    
    def _monitor_sms(self):
        """短信监听核心（原有逻辑，稍作适配）"""
        police_keywords = [
            "交警", "交管12123", "未按规定停放", "立即驶离",
            "依法予以处罚", "违停", "抄牌", "挪车", "违法停车"
        ]
        
        while self.monitor_running and self.plate_list:
            try:
                sms_list = droid.smsGetMessages(True, "inbox").result
                if sms_list and len(sms_list) > 0:
                    latest_sms = sms_list[-1]
                    sms_sender = latest_sms.get('address', '').strip()
                    sms_content = latest_sms.get('body', '').strip()
                    current_time = time.time()
                    
                    match_plate = None
                    for plate in self.plate_list:
                        if plate in sms_content:
                            match_plate = plate
                            break
                    
                    is_target = (
                        match_plate is not None
                        and ("交警" in sms_sender or "12123" in sms_sender)
                        and any(key in sms_content for key in police_keywords)
                        and (match_plate not in self.last_alert_time or
                             current_time - self.last_alert_time[match_plate] > self.ALERT_INTERVAL)
                    )
                    
                    if is_target:
                        self.last_alert_time[match_plate] = current_time
                        
                        # 震动
                        vibrator.vibrate(self.alert_config["vibrate_time"] / 1000)
                        
                        # 通知
                        notification.notify(
                            title="🚨 紧急挪车提醒",
                            message=f"你的车牌 {match_plate} 涉嫌违停！",
                            app_name="搬车APP",
                            timeout=10
                        )
                        
                        # 语音
                        for i in range(self.alert_config["play_times"]):
                            if not self.monitor_running:
                                break
                            tts.speak(self.alert_config["voice_text"])
                            if i < self.alert_config["play_times"] - 1:
                                time.sleep(2)
            
            except Exception as e:
                print(f"监听异常：{e}")
            time.sleep(3)
    
    def test_alert(self, plate):
        """测试提醒"""
        # 震动
        vibrator.vibrate(self.alert_config["vibrate_time"] / 1000)
        
        # 通知
        notification.notify(
            title="🚨 测试提醒",
            message=f"这是测试提醒，监控车牌 {plate}",
            app_name="搬车APP",
            timeout=5
        )
        
        # 语音
        tts.speak("这是测试提醒")


if __name__ == "__main__":
    CheCarApp().run()