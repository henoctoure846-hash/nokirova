[app]
title = NOKIROVA
package.name = nokirova
package.domain = org.nokirova

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = fonts/*,assets/*
source.main = mobile_app.py

version = 1.0

requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.1.1,pillow,requests,certifi,charset-normalizer,urllib3,idna,httpx,httpcore,h11,anyio,sniffio,typing-extensions

orientation = portrait
fullscreen = 0

# 🎨 ICÔNE & SPLASH SCREEN
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/icon.png

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.build_tools_version = 33.0.2
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

# 🔧 Forcer une version stable de python-for-android (Python 3.11 compatible Kivy)
p4a.branch = 2024.01.21
p4a.fork = kivy

[buildozer]
log_level = 2
warn_on_root = 0