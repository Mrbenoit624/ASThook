# !/bin/bash
set -x
# setup frida-server

VERSION_FRIDA="12.11.18"

cd bin

for abi in "x86" "x86_64" "arm" "arm64";
do
  echo "Install frida server for ${abi}"
  wget --quiet "https://github.com/frida/frida/releases/download/${VERSION_FRIDA}/frida-server-${VERSION_FRIDA}-android-${abi}.xz"
  xzcat "frida-server-${VERSION_FRIDA}-android-${abi}.xz" > frida-server_${abi}
  rm frida-server-${VERSION_FRIDA}-android-${abi}.xz
done

cd ..
