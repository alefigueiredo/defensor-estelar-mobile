[app]
title = Defensor Estelar
package.name = defensorestelar
package.domain = org.spacearcade
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 1
android.permissions = VIBRATE
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1

