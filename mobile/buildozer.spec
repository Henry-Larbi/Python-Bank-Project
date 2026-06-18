[app]
title = Access Bank
package.name = accessbank
package.domain = com.accessbank

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = ../config.py,../db.py,../email_service.py

version = 1.0

requirements = python3,kivy,kivymd,psycopg2,certifi,urllib3,charset-normalizer,idna

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
