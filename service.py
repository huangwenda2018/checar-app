# -*- coding: utf-8 -*-
from android import service
from androidhelper import Android
import threading
import time

droid = Android()

class CarAlertService(service.Service):
    def onStartCommand(self, intent, flags, startId):
        try:
            notification = droid.makeNotification(
                title="搬车APP正在运行",
                content="正在监听交警挪车短信",
            ).result
            droid.startForeground(1, notification)
            
            def start_app():
                try:
                    from main import CheCarApp
                    self.app = CheCarApp()
                    self.app.plate_list = ["京A12345", "粤B88888"]
                    self.app.start_monitor(self.app.plate_list)
                    while True:
                        time.sleep(60)
                except Exception as e:
                    print(f"应用启动失败: {e}")
            
            threading.Thread(target=start_app, daemon=True).start()
        except Exception as e:
            print(f"服务启动失败: {e}")
        
        return service.Service.START_STICKY
    
    def onDestroy(self):
        try:
            if hasattr(self, 'app'):
                self.app.stop_monitor()
        except:
            pass
        super().onDestroy()

