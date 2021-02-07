from urllib.request import urlretrieve
import lzma
from asthook.conf import PACKAGE_PATH, VERSION_FRIDA
import tempfile


def main():
    with tempfile.TemporaryDirectory() as tmpdirname:
        for _type, _ext in [("server", ""), ("gadget", ".so")]:
            for abi in ["x86", "x86_64", "arm", "arm64"]:
                print(f"Install frida {_type} for {abi}")
                url = f"https://github.com/frida/frida/releases/download/{VERSION_FRIDA}/frida-{_type}-{VERSION_FRIDA}-android-{abi}{_ext}.xz"
                urlretrieve(url, f"{tmpdirname}/frida-{_type}{_ext}.xz")
                with open(f"{PACKAGE_PATH}/bin/frida-{_type}_{abi}{_ext}", "wb") as fw:
                    with lzma.open(f"{tmpdirname}/frida-{_type}{_ext}.xz") as fr:
                        fw.write(fr.read())

if __name__ == "__main__":
    main()
