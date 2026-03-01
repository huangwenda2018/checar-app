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

# 依赖库 - 完全移除 pyjnius
requirements = python3==3.8.10, kivy==2.1.0, android, plyer

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
android.api = 30
android.minapi = 21

# 指定稳定的 build-tools 版本
android.build_tools = 30.0.3

# 其他
android.wakelock = True
android.ndk = 23b
android.sdk = 30

# 自动接受许可证
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
