# -*- coding: utf-8 -*-
"""
Android 前台服务
确保应用在后台不被系统杀死
"""
from android import service
from androidhelper import Android
import threading
import time

droid = Android()

class CarAlertService(service.Service):
    def onStartCommand(self, intent, flags, startId):
        """服务启动时调用"""
        try:
            # 创建通知
            notification = droid.makeNotification(
                title="搬车APP正在运行",
                content="正在监听交警挪车短信",
            ).result
            
            # 启动前台服务 (Android 8.0+ 必需)
            droid.startForeground(1, notification)
            
            # 在新线程中启动主逻辑
            def start_app():
                try:
                    from main import CheCarApp
                    self.app = CheCarApp()
                    self.app.load_plates()
                    self.app.start_monitor()
                    
                    # 保持服务运行
                    while True:
                        time.sleep(60)
                except Exception as e:
                    print(f"应用启动失败: {e}")
            
            thread = threading.Thread(target=start_app, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"前台服务启动失败: {e}")
        
        # 返回 START_STICKY 表示服务被杀死后会自动重启
        return service.Service.START_STICKY
    
    def onDestroy(self):
        """服务销毁时"""
        try:
            if hasattr(self, 'app'):
                self.app.stop_monitor()
        except:
            pass
        super().onDestroy()
