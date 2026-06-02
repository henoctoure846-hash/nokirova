[app]
title = NOKIROVA
package.name = nokirova
package.domain = org.nokirova

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = fonts/*

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,certifi,charset-normalizer,urllib3,idna,groq,google-generativeai,httpx,h11,anyio,sniffio,distro,pydantic,typing-extensions

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1