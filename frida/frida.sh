#!/bin/bash

javac Frida.java

/usr/lib/android-sdk/build-tools/debian/dx --dex --output classes.dex Frida.class

rm Frida.zip

zip Frida.zip classes.dex

adb push Frida.zip /data/local/tmp/Frida.zip

# dalvikvm -cp /data/local/tmp/Frida.zip Frida 


# frida -D emulator-5554 -l test.js -f com.example.apkwithoutsllpinning --no-pause
