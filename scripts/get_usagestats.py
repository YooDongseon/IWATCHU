
from ppadb.client import Client as AdbClient

client = AdbClient(host='127.0.0.1', port=5037)
devices = client.devices()
device1 = devices[0]

print("잠시만 기다려 주세요.")
device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
device1.pull("sdcard/usagestats_result.txt", "c:\\users\\jsj97\\desktop\\script_result\\usagestats_result.txt")
device1.shell("rm sdcard/usagestats_result.txt")

