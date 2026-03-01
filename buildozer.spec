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

# 依赖库
requirements = python3==3.11.0, kivy==2.1.0, android, pyjnius==1.6.1, plyer, cython

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

# 关键修复：指定 build-tools 版本为稳定版
android.build_tools = 34.0.0

# 添加这些可以加速打包（可选）
android.accept_sdk_license = True
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk

