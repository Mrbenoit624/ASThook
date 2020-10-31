# To use it outside the script add the ENV variable VERSION
#VERSION=29.0.3
# To use it outside the script add the ENV variable SDK_TOOLS
#SDK_TOOLS=/usr/lib/android-sdk/

{% if version|length %}VERSION={{ version }}{% endif %}
{% if sdktools|length %}SDK_TOOLS={{ sdktools }}{% endif %}


APP=exploit

VERSION_B=$(basename $(basename $(VERSION)))

pass=ahahah

all: $(shell mkdir build res)
all: build/$(APP).apk


res:
	$(SDK_TOOLS)/build-tools/$(VERSION)/aapt package -v -f -m  -S ./res -J ./src -M ./AndroidManifest.xml -I "$(SDK_TOOLS)/platforms/android-$(VERSION_B)/android.jar"

class: res
class: $(shell find java -type f -regex ".*\.java")
	javac -d ./build -classpath $(SDK_TOOLS)/platforms/android-$(VERSION_B)/android.jar -sourcepath ./java $<

build/classes.dex: class
build/classes.dex: $(shell find build -type f -regex ".*\.class")
	$(SDK_TOOLS)/build-tools/$(VERSION)/dx --dex --verbose --output=$@ ./build

build/%.unsigned.apk: build/classes.dex
	$(SDK_TOOLS)/build-tools/$(VERSION)/aapt package -v -f -M ./AndroidManifest.xml -S ./res -I $(SDK_TOOLS)/platforms/android-$(VERSION_B)/android.jar -F $@ ./build

build/%.signed.apk:./build/%.unsigned.apk ./ToyKey.keystore
	jarsigner -verbose -keystore ./ToyKey.keystore -storepass $(pass) -keypass $(pass) -signedjar $@ $< MadKey

build/%.apk :  ./build/%.signed.apk
	$(SDK_TOOLS)/build-tools/$(VERSION)/zipalign -v -f 4 $< $@


ToyKey.keystore :
	keytool -genkeypair -validity 1000 -dname "CN=MadSquirrel,O=Android,C=FR" -keystore $@ -storepass $(pass) -keypass $(pass) -alias MadKey -keyalg RSA -v

clean:
	$(RM) -r build/* ToyKey.keystore
