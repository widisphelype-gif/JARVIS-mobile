[app]
title = VLAD AI
package.name = vladiaapp
package.domain = org.shadows
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# MUDANÇA CRÍTICA AQUI: Forçando o uso do Python 3.11.5 estável
requirements = python3==3.11.5,kivy==2.3.0,requests,urllib3,chardet,idna

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.allow_backup = True
android.api = 33
