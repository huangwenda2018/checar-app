[app]

# 应用基本信息
title = 搬车APP
package.name = checar
package.domain = org.example

# 源码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

# 版本
version = 0.1
version.release = 0.1

# 依赖库 (重要！)
requirements = python3==3.11.0, android, pyjnius, plyer

# 权限
android.permissions = READ_SMS, RECEIVE_SMS, VIBRATE, POST_NOTIFICATIONS, FOREGROUND_SERVICE

# 服务声明
android.services = CarAlertService:service.py
android.foreground_service = CarAlertService

# 图标
icon.filename = icon.png
presplash.filename = banner.png

# 架构
android.arch = arm64-v8a
android.api = 33
android.minapi = 21

# 其他
android.wakelock = True
android.ndk = 25b
android.sdk = 33
