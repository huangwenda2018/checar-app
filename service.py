# -*- coding: utf-8 -*-
from android import service
from androidhelper import Android
import threading

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
                from main import CheCarApp
                self.app = CheCarApp()
                self.app.load_plates()
                self.app.start_monitor()
            
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