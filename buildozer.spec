[app]

title = 搬车APP
package.name = checar
package.domain = com.yourname

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json

version = 0.1
version.release = 0.1

requirements = python3, android, androidhelper, plyer, kivy==2.1.0

android.permissions = READ_SMS, RECEIVE_SMS, VIBRATE, POST_NOTIFICATIONS, FOREGROUND_SERVICE, WAKE_LOCK

android.services = CarAlertService:service.py
android.foreground_service = CarAlertService

icon.filename = icon.png
presplash.filename = banner.png

android.arch = arm64-v8a
android.api = 33
android.minapi = 21
android.wakelock = True