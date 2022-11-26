from ppadb.client import Client as AdbClient
import os

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating director.y" + directory)

client = AdbClient(host='127.0.0.1', port=5037)
devices = client.devices()
device1 = devices[0]

print("설치된 서드파티 apk 파일 확인 중...")
device1.shell("pm list packages -3 -f > data/local/tmp/installed_apk_list.txt")
device1.pull("data/local/tmp/installed_apk_list.txt", "c:\\users\\jsj97\\desktop\\script_result\\installed_apk_list.txt")

with open("c:\\users\\jsj97\\desktop\\script_result\\installed_apk_list.txt") as f:
    lines = f.readlines()

installed_packages=[]

for i in range(len(lines)):
    installed_packages.append(lines[i].replace("package:","").replace("\n","").split("apk"))

print("설치된 서드파티 apk 파일 추출 중...")
for z in range(len(installed_packages)):
    createFolder("C:/users//jsj97/desktop/script_result/extracted_apk/{}".format(installed_packages[z][1]))
    device1.pull("/{}apk".format(installed_packages[z][0]), "C:/users/jsj97/desktop/script_result/extracted_apk/{}/base.apk".format(installed_packages[z][1]))

print("설치된 서드 파티 apk 파일 추출 완료")
device1.shell("rm data/local/tmp/installed_apk_list.txt")