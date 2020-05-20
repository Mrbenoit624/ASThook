
adb jdwp
# last uid = last app launched

adb forward tcp:7777 jdwp:<uid>
jdb -attach localhost:7777
