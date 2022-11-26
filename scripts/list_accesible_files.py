from ppadb.client import Client as AdbClient
import subprocess
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

print("1분 정도의 시간이 소요될 수 있습니다. 잠시만 기다려 주세요.")
device1.shell("du -a > sdcard/accesible_file_list.txt")
device1.pull("sdcard/accesible_file_list.txt", "c:\\users\\jsj97\\desktop\\script_result\\accesible_file_list.txt")
print("접근 가능 목록 추출이 완료되었습니다.")

f = open("c:\\users\\jsj97\\desktop\\script_result\\accesible_file_list.txt", "rt", encoding='UTF8')
lines = f.readlines()

accessible_files=[]

for i in range(len(lines)):
    accessible_files.append(lines[i].replace("package:","").replace("\n","").split("\t"))

print(accessible_files)
for z in range(len(accessible_files)):
    print("진행률 : {}/{}".format(z, len(accessible_files)))
    subprocess.call("adb pull {} C:\\Users\\jsj97\\Desktop\\script_result\\accessible_file".format(accessible_files[z][1], shell=True))

print("추출 완료")