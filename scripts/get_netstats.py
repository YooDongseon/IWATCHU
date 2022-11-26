
from ppadb.client import Client as AdbClient
from datetime import datetime

client = AdbClient(host='127.0.0.1', port=5037)
devices = client.devices()
device1 = devices[0]

device1.shell("dumpsys netstats | grep -v 'iface' > sdcard/network_list.txt")
device1.pull("sdcard/network_list.txt", "c:\\users\\jsj97\\desktop\\script_result\\network_list.txt")
device1.shell("rm sdcard/network_list.txt")

p = open("c:\\users\\jsj97\\desktop\\script_result\\network_list.txt", "r", encoding='utf-8')
f = open("c:\\users\\jsj97\\desktop\\script_result\\network_info.txt", "a", encoding='utf-8')

#netstat에 grep 한 결과물 리스트화
lines=p.readlines()

select = []

#필요한 로그만 select 리스트에 수집
for i in range(len(lines)):
    if "ident" in lines[i]:
        if "networkId" in lines[i]:
            select.append(lines[i].split(","))
    if "st=" in lines[i]:
        select.append(lines[i])

#네트워크 ID만 수집
only_networkId=[]
for i in range(len(select)):
    if "networkId" in select[i][2]:
        only_networkId.append(select[i][2])
#네트워크 ID 정렬
only_networkId2=set(only_networkId)
only_networkId3=list(only_networkId2)

#네트워크 목록 작성
f.write("연결된 네트워크 목록\n")
for i in range(len(only_networkId3)):
    f.write("{}. {}\n".format(i+1, only_networkId3[i].replace("networkId=", "")))

#세부사항 작성
f.write("\n세부사항\n")

detail_info =[]
for i in range(len(select)):
    if "networkId" in select[i][2]:
        detail_info.append(select[i][2])
    if "st=" in select[i]:
        detail_info.append(select[i].split(" "))

#리스트 내 숫자 문자열 정수형으로 변환
modify=[]
for i in range(len(detail_info)):
    if "st=" in detail_info[i][6]:
        modify_element=[]
        modify_element.append(detail_info[i][6].replace("st=", ""))
        modify_element.append(detail_info[i][7].replace("rb=", ""))
        modify_element.append(detail_info[i][8].replace("rp=", ""))
        modify_element.append(detail_info[i][9].replace("tb=", ""))
        modify_element.append(detail_info[i][10].replace("tp=", ""))
        int_modify = list(map(int, modify_element))
        modify.append(int_modify)
    else:
        modify.append(detail_info[i])

num=1
for i in range(len(modify)):
    if "networkId" in modify[i]:
        f.write("{}. {}\n".format(num, modify[i].replace("networkId=", "")))
        num+=1
    else:
        f.write("\t통신시각: {}   다운로드: {}byte   다운로드 패킷: {}개   업로드: {}byte   업로드 패킷: {}개\n".format(datetime.fromtimestamp(modify[i][0]), modify[i][1], modify[i][2], modify[i][3], modify[i][4]))