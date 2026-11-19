[app]
title = Guvende
package.name = guvende
package.domain = az.guvende
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db,sqlite3
version = 0.1
requirements = python3,kivy,requests,certifi,urllib3,idna,charset-normalizer,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
