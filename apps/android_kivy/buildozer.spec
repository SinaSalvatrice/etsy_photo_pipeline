[app]
title = Etsy Photo Pipeline
package.name = etsyphotopipeline
package.domain = org.circuitcurios
source.dir = ../..
source.include_exts = py,png,jpg,jpeg,webp,json,md,txt
source.exclude_dirs = .venv,venv,output,dist,build,__pycache__
version = 0.1
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 35
android.minapi = 23
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
