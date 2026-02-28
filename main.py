# -*- coding: utf-8 -*-
"""
搬车APP - 交警挪车短信监听核心
"""
import time
import threading
import json
import os
from androidhelper import Android
from plyer import notification, vibrator, tts

droid = Android()

class CheCarApp:
    def __init__(self):
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
        self.config_file = "/sdcard/checar_config.json"

    def load_plates(self):
        """加载车牌列表"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.plate_list = config.get('plates', [])
                    self.alert_config.update(config.get('alert_config', {}))
            else:
                self.plate_list = ["京A12345", "粤B88888"]
                self.save_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.plate_list = ["京A12345", "粤B88888"]

    def save_config(self):
        """保存配置"""
        try:
            config = {
                'plates': self.plate_list,
                'alert_config': self.alert_config
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def start_monitor(self):
        """启动监听"""
        if not self.plate_list:
            return False
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_sms, daemon=True)
        self.monitor_thread.start()
        return True

    def stop_monitor(self):
        self.monitor_running = False

    def _monitor_sms(self):
        """短信监听核心"""
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


if __name__ == "__main__":
    app = CheCarApp()
    app.load_plates()
    app.start_monitor()
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        app.stop_monitor()