[app]
title = NOKIROVA
package.name = nokirova
package.domain = org.nokirova

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = fonts/*
source.main = mobile_app.py

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,certifi,charset-normalizer,urllib3,idna,groq,google-generativeai,httpx,httpcore,h11,anyio,sniffio,distro,pydantic,pydantic-core,typing-extensions,annotated-types

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.build_tools_version = 33.0.2
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0