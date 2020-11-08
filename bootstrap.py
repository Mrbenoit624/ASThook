from urllib.request import urlretrieve
import lzma
from asthook.conf import PACKAGE_PATH, VERSION_FRIDA


def main():
    for abi in ["x86", "x86_64", "arm", "arm64"]:
        print(f"Install frida server for {abi}")
        url = f"https://github.com/frida/frida/releases/download/{VERSION_FRIDA}/frida-server-{VERSION_FRIDA}-android-{abi}.xz"
        urlretrieve(url, f"/tmp/frida-server.xz")
        with open(f"{PACKAGE_PATH}/bin/frida-server_{abi}", "wb") as fw:
                with lzma.open(f"/tmp/frida-server.xz") as fr:
                    fw.write(fr.read())

if __name__ == "__main__":
    main()
