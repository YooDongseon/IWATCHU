import argparse
import os
from ppadb.client import Client as AdbClient
from datetime import datetime
import time 
import subprocess
import pandas as pd
import sys
from exif import Image
import folium
import webbrowser
from elasticsearch import helpers
from elasticsearch_dsl import connections

def main():                                                                                                                                    # Wear OS 메인

    def createFolder(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print("Error: Creating director.y" + directory)
    
    def dockercheck():
        try:
            a = subprocess.check_output("docker ps -a")
            b = a.decode('utf-8')
            c = b.replace("\n","  ").split('  ')
            while '' in c:
                c.remove('')   
            find_str = 'Up'
            find_up = [i for i in range(len(c)) if find_str in c[i]]
            if len(find_up) == 0:
                sys.exit()    
            for i in find_up:
                print(i)
                docker_name = c[i + 2]
                if docker_name[1:11] != "docker-elk":
                    sys.exit()
        
        except:
            print("Check your docker environment")
            sys.exit()
     
    Select = argparse.ArgumentParser(description='Smart Watch analyzer for Wear OS')
    Select.add_argument("Wear", action='store') 
    Select.add_argument("--apk", dest="woapk", action='store_true', help="At Wear os, extract apk files")  
    Select.add_argument("--network", dest="wonet", action='store_true', help="At Wear os, get network stats")
    Select.add_argument("--package", dest="wopack", action='store_true', help="At Wear os, get package information") 
    Select.add_argument("--usage", dest="wouse", action='store_true', help="At Wear os, get information of Application usage statistic")
    Select.add_argument("--access", dest="woacc", action='store_true', help="At Wear os, list accessible file")
    Select.add_argument("--picture", dest="wopic", action='store_true', help="At Wear os, get a location information of picture where it taken")
    Select.add_argument("--del", dest="wodel", action='store_true', help="At Wear os, list a deleted package name")
    Select.add_argument("--all", dest="woall", action='store_true', help="At Wear os, get a all information advertised at above")
    arge = Select.parse_args()
    
    
    if arge.woapk:
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\application".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\extracted_apk".format(os.getcwd()))
        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("설치된 apk 파일 확인 중...")
            device1.shell("pm list packages -f > data/local/tmp/installed_apk_list.txt")
            device1.pull("data/local/tmp/installed_apk_list.txt", "{}\\IWATCHU\\WearOS\\application\\installed_apk_list.txt".format(os.getcwd()))

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("설치된 apk 파일 확인 중...")
            device1.shell("pm list packages -f > data/local/tmp/installed_apk_list.txt")
            device1.pull("data/local/tmp/installed_apk_list.txt", "{}\\IWATCHU\\WearOS\\application\\installed_apk_list.txt".format(os.getcwd()))

        with open("{}\\IWATCHU\\WearOS\\application\\installed_apk_list.txt".format(os.getcwd())) as f:
            lines = f.readlines()

        installed_packages=[]

        for i in range(len(lines)):
            installed_packages.append(lines[i].replace("package:","").replace("\n","").split("apk"))

        #permission denied 발생 이유는 복사하려는 기존 파일이 복사해서 들어올 때 파일 명을 안정해줘서 그런거임.
        print("설치된 apk 파일 추출 중...")
        for z in range(len(installed_packages)):
            createFolder("{}/IWATCHU/extracted_apk/{}".format(os.getcwd(),installed_packages[z][1]))
            device1.pull("/{}apk".format(installed_packages[z][0]), "{}/IWATCHU/extracted_apk/{}/base.apk".format(os.getcwd(),installed_packages[z][1]))

        print("설치된 apk 파일 추출 완료")
        device1.shell("rm data/local/tmp/installed_apk_list.txt")
        
    if arge.wonet:
        
        def netstats_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_netstats',
                    "_type"  : "_doc",
                    "_source" : document
                }
        
        es_client = connections.create_connection(hosts=['elastic:changeme@127.0.0.1:9200'])
        datetime_format="%Y-%m-%d %H:%M:%S"
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\netstats\\".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("dumpsys netstats | grep -v 'iface' > sdcard/network_list.txt")
            device1.pull("sdcard/network_list.txt", "{}\\IWATCHU\\WearOS\\netstats\\network_list.txt".format(os.getcwd()))
            device1.shell("rm sdcard/network_list.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("dumpsys netstats | grep -v 'iface' > sdcard/network_list.txt")
            device1.pull("sdcard/network_list.txt", "{}\\IWATCHU\\WearOS\\netstats\\network_list.txt".format(os.getcwd()))
            device1.shell("rm sdcard/network_list.txt")

        p = open("{}\\IWATCHU\\WearOS\\netstats\\network_list.txt".format(os.getcwd()), "r", encoding='utf-8')
        f = open("{}\\IWATCHU\\WearOS\\netstats\\network_info.txt".format(os.getcwd()), "a", encoding='utf-8')

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


        #csv로 출력하기
        netstats={}
        networkId_array=[]
        connected_datetime=[]
        connected_timestamp=[]
        download_byte=[]
        download_packet=[]
        upload_byte=[]
        upload_packet=[]
        for i in range(len(modify)):
            if 'networkId' in modify[i]:
                networkId=str(modify[i].replace(' networkId=',"").replace('\"',"").replace('<',"").replace('>',""))
            else:
                networkId_array.append(networkId)
                connected_datetime.append(str(datetime.fromtimestamp(modify[i][0])))
                connected_timestamp.append(str(modify[i][0]))
                download_byte.append(str(modify[i][1]))
                download_packet.append(str(modify[i][2]))
                upload_byte.append(str(modify[i][3]))
                upload_packet.append(str(modify[i][4]))

        netstats['networkId']=networkId_array
        netstats['connected_datetime']=connected_datetime
        netstats['connected_timestamp']=connected_timestamp
        netstats['download_byte']=download_byte
        netstats['download_packet']=download_packet
        netstats['upload_byte']=upload_byte
        netstats['upload_packet']=upload_packet

        df_net=pd.DataFrame(netstats)
        df_net.to_csv("{}\\IWATCHU\\WearOS\\netstats\\fin_netstats.csv".format(os.getcwd()))

        new_netstats=[]
        for i in range(len(modify)):
            if 'networkId' in modify[i]:
                networkId=str(modify[i].replace(' networkId=',"").replace('\"',"").replace('<',"").replace('>',""))
            else:
                data=[networkId, datetime.fromtimestamp(modify[i][0]), modify[i][0], modify[i][1], modify[i][2], modify[i][3], modify[i][4]]
                new_netstats.append(data)

        elk_netstats = pd.DataFrame(new_netstats, columns =['networkId', 'connected_datetime', 'connected_timestamp', 'download_byte', 'download_packet', 'upload_byte', 'uploda_packet'])
        dockercheck()
        print("netstats elk 서버 전송 중...")
        helpers.bulk(es_client, netstats_generator(elk_netstats))
        
    if arge.wopack:
        
        def app_info_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_3rd_application_info',
                    "_type"  : "_doc",
                    "_source" : document
                }
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\application".format(os.getcwd()))

        es_client = connections.create_connection(hosts=['elastic:changeme@127.0.0.1:9200'])
        datetime_format="%Y-%m-%d %H:%M:%S"

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]
            installed_packages=[]

            device1.shell("pm list packages -3 > data/local/tmp/3rd_package_list.txt")
            device1.pull("data/local/tmp/3rd_package_list.txt", "{}\\IWATCHU\\WearOS\\application\\3rd_package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/3rd_package_list.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("pm list packages -3 > data/local/tmp/3rd_package_list.txt")
            device1.pull("data/local/tmp/3rd_package_list.txt", "{}\\IWATCHU\\WearOS\\application\\3rd_package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/3rd_package_list.txt")

        p=open("{}\\IWATCHU\\WearOS\\application\\3rd_package_list.txt".format(os.getcwd()), "r")

        lines = p.readlines()

        package_info=[]
        firstInstallLine=0
        req_perm_start=0
        req_perm_end=0
        install_time=[]
        for i in range(len(lines)):
            app_name=lines[i].replace("package:", "").replace("\n","")
            device1.shell("dumpsys package {} > data/local/tmp/{}_dumpsys.txt".format(app_name, app_name))
            device1.pull("data/local/tmp/{}_dumpsys.txt".format(app_name),  "{}\\IWATCHU\\WearOS\\application\\{}_dumpsys.txt".format(os.getcwd(), app_name))
            device1.shell("rm dumpsys package {}".format(app_name, app_name))
            f=open("{}\\IWATCHU\\WearOS\\application\\{}_dumpsys.txt".format(os.getcwd(), app_name), "r")
            package_lines=f.readlines()
            for z in range(len(package_lines)):
                if "firstInstallTime" in package_lines[z]:
                    firstInstallLine=z
                    install_time.append(package_lines[firstInstallLine].split(" "))
                if "requested permissions:" in package_lines[z]:
                    req_perm_start=z+1
                if "install permissions:" in package_lines[z]:
                    req_perm_end=z
            
            for q in range(req_perm_start, req_perm_end):
                dateTime=datetime.strptime("{} {}".format(install_time[i][4].replace("firstInstallTime=",""), install_time[i][5].replace("\n","")), datetime_format)
                package_info.append([str(app_name), dateTime , str(package_lines[q].replace(" ","").replace("\n",""))])

        third_package_info = pd.DataFrame(package_info, columns =['app_name', 'firstInstallTime', 'requested permission'])
        dockercheck()
        print("서드파티 앱 정보 elk 서버 전송 중...")
        helpers.bulk(es_client, app_info_generator(third_package_info))
        
    if arge.wouse:
        def daily_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_daily_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }

        def weekly_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_weekly_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }

        def monthly_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_monthly_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }

        def yearly_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_yearly_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }
                
        es_client = connections.create_connection(hosts=['elastic:changeme@127.0.0.1:9200'])
        datetime_format="%Y-%m-%d %H:%M:%S"
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\usagestats".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("잠시만 기다려 주세요.")
            device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
            device1.pull("sdcard/usagestats_result.txt", "{}\\IWATCHU\\WearOS\\usagestats\\usagestats_result.txt".format(os.getcwd()))
            device1.shell("rm sdcard/usagestats_result.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("잠시만 기다려 주세요. 네트워크 로그 수집 중...")
            device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
            device1.pull("sdcard/usagestats_result.txt", "{}\\IWATCHU\\WearOS\\usagestats\\usagestats_result.txt".format(os.getcwd()))
            device1.shell("rm sdcard/usagestats_result.txt")
        
        f = open("{}\\IWATCHU\\WearOS\\usagestats\\usagestats_result.txt".format(os.getcwd()), "r", encoding='utf-8')
        lines = f.readlines()


        #24시간 usagestats
        collect_24h = []

        for i in range(len(lines)):
            if "time=" in lines[i]:
                collect_24h.append(lines[i].split(" "))

        daily_usage={}
        daily_datetime=[]
        daily_timestamp=[]
        daily_status=[]
        daily_appname=[]

        #daily usagestats csv
        print("daily usagestats 파싱 중...")
        for i in range(len(collect_24h)):
            stringtime="{} {}".format(str(collect_24h[i][4]).replace('time="', ''), str(collect_24h[i][5]).replace('"',''))
            daily_datetime.append(stringtime)
            daily_timestamp.append("{}".format(time.mktime(datetime.strptime(stringtime, '%Y-%m-%d %H:%M:%S').timetuple())))
            daily_status.append(collect_24h[i][6].replace("type=",""))
            daily_appname.append(collect_24h[i][7].replace("package=", ""))

        daily_usage['datetime']=daily_datetime
        daily_usage['timestamp']=daily_timestamp
        daily_usage['status']=daily_status
        daily_usage['appname']=daily_appname

        df_day=pd.DataFrame(daily_usage)
        df_day.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_daily_usagestats.csv".format(os.getcwd()))

        #daily usagestats elk
        new_day=[]
        for i in range(len(collect_24h)):
            data=[]
            stringtime="{} {}".format(str(collect_24h[i][4]).replace('time="', ''), str(collect_24h[i][5]).replace('"',''))
            toDateTime=datetime.strptime(stringtime, datetime_format)
            data.append(toDateTime)
            data.append(collect_24h[i][7].replace("package=", ""))
            data.append("{}".format(time.mktime(datetime.strptime(stringtime, '%Y-%m-%d %H:%M:%S').timetuple())))
            data.append(collect_24h[i][6].replace("type=",""))
            new_day.append(data)

        new_df_day = pd.DataFrame(new_day, columns =['datetime', 'app_name', 'timestamp', 'status'])
        dockercheck()
        print("daily usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, daily_doc_generator(new_df_day))

        #주, 월, 년 별 사용 내역이 담긴 열의 범위 확인
        ChooserCounts_num =0
        weekly_start=0
        weekly_end=0

        monthly_start=0
        monthly_end=0

        yearly_start=0
        yearly_end=0

        for i in range(len(lines)):
            if "In-memory weekly stats" in lines[i]:
                weekly_start=i
            if "In-memory monthly stats" in lines[i]:
                monthly_start=i
            if "In-memory yearly stats" in lines[i]:
                yearly_start=i
            if "ChooserCounts" in lines[i]:
                ChooserCounts_num += 1
                if ChooserCounts_num == 2:
                    weekly_end = i - 2
                if ChooserCounts_num == 3:
                    monthly_end = i -2
                if ChooserCounts_num == 4:
                    yearly_end = i -2
                
        #주, 월, 년 별 범위를 각각의 리스트에 저장
        collect_week=[]
        collect_month=[]
        collect_year=[]

        for i in range(weekly_start, weekly_end+1):
            if "package=" in lines[i]:
                collect_week.append(lines[i].split(" "))

        for i in range(monthly_start, monthly_end+1):
            if "package=" in lines[i]:
                collect_month.append(lines[i].split(" "))

        for i in range(yearly_start, yearly_end+1):
            if "package=" in lines[i]:
                collect_year.append(lines[i].split(" "))

        #print(lines[weekly_start])
        #print(collect_week[0])
        #print(collect_month[0])
        #print(collect_year[0])

        #week csv
        print("weekly usagestats 파싱 중...")
        weekly_usage={}
        weekly_app_name=[] 
        weekly_totalTimeUsed =[]
        weekly_lastTimeUsed=[] 
        weekly_totalTimeVisible=[] 
        weekly_lastTimeVisible=[]
        for i in range(len(collect_week)):
            weekly_app_name.append(collect_week[i][6].replace("package=",""))
            weekly_totalTimeUsed.append(collect_week[i][7].replace("totalTimeUsed=", "").replace('"',''))
            weekly_lastTimeUsed.append("{} {}".format(collect_week[i][8].replace("lastTimeUsed=","").replace('"',''), collect_week[i][9]).replace('"',''))
            weekly_totalTimeVisible.append(collect_week[i][10].replace("totalTimeVisible=", "").replace('"',''))
            weekly_lastTimeVisible.append("{} {}".format(collect_week[i][11].replace("lastTimeVisible=","").replace('"',''), collect_week[i][12]).replace('"',''))

        weekly_usage['app_name']=weekly_app_name
        weekly_usage['totalTimeUsed']=weekly_totalTimeUsed
        weekly_usage['lastTimeUsed']=weekly_lastTimeUsed
        weekly_usage['totalTimeVisible']=weekly_totalTimeVisible
        weekly_usage['lastTimeVisible']=weekly_lastTimeVisible

        df_week=pd.DataFrame(weekly_usage)
        df_week.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_weekly_usagestats.csv".format(os.getcwd()))

        #elk 바로 업로드
        new_week=[]
        for i in range(len(collect_week)):
            string_last_time="{} {}".format(collect_week[i][8].replace("lastTimeUsed=","").replace('"',''), collect_week[i][9]).replace('"','')
            dateTime=datetime.strptime(string_last_time, datetime_format)
            string_visible_time="{} {}".format(collect_week[i][11].replace("lastTimeVisible=","").replace('"',''), collect_week[i][12]).replace('"','')
            lastTime=dateTime.strptime(string_visible_time, datetime_format)
            data=[]
            data.append(collect_week[i][6].replace("package=",""))
            data.append(collect_week[i][7].replace("totalTimeUsed=", "").replace('"',''))
            data.append(dateTime)
            data.append(collect_week[i][10].replace("totalTimeVisible=", "").replace('"',''))
            data.append(lastTime)
            new_week.append(data)

        new_df_week = pd.DataFrame(new_week, columns =['app_name', 'totalTimeUsed', 'lastTimeUsed', 'totalTimeVisible', 'lastTimeVisible'])
        dockercheck()
        print("weekly usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, weekly_doc_generator(new_df_week))

        #month csv
        print("monthly usagestats 파싱 중...")
        monthly_usage={}
        monthly_app_name=[]
        monthly_totalTimeUsed=[]
        monthly_lastTimeUsed=[]
        monthly_totalTimeVisible=[]
        monthly_lastTimeVisible=[]
        for i in range(len(collect_month)):
            monthly_app_name.append(collect_month[i][6].replace("package=",""))
            monthly_totalTimeUsed.append(collect_month[i][7].replace("totalTimeUsed=", "").replace('"',''))
            monthly_lastTimeUsed.append("{} {}".format(collect_month[i][8].replace("lastTimeUsed=","").replace('"',''), collect_month[i][9]).replace('"',''))
            monthly_totalTimeVisible.append(collect_month[i][10].replace("totalTimeVisible=", "").replace('"',''))
            monthly_lastTimeVisible.append("{} {}".format(collect_month[i][11].replace("lastTimeVisible=","").replace('"',''), collect_month[i][12]).replace('"',''))

        monthly_usage['app_name']=monthly_app_name
        monthly_usage['totalTimeUsed']=monthly_totalTimeUsed
        monthly_usage['lastTimeUsed']=monthly_lastTimeUsed
        monthly_usage['totalTimeVisible']=monthly_totalTimeVisible
        monthly_usage['lastTimeVisible']=monthly_lastTimeVisible

        df_month=pd.DataFrame(monthly_usage)
        df_month.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_monthly_usagestats.csv".format(os.getcwd()))

        #elk 바로 업로드
        new_month=[]
        for i in range(len(collect_month)):
            data=[]
            string_last_time="{} {}".format(collect_month[i][8].replace("lastTimeUsed=","").replace('"',''), collect_month[i][9]).replace('"','')
            dateTime=datetime.strptime(string_last_time, datetime_format)
            string_visible_time="{} {}".format(collect_month[i][11].replace("lastTimeVisible=","").replace('"',''), collect_month[i][12]).replace('"','')
            lastTime=dateTime.strptime(string_visible_time, datetime_format)
            data.append(collect_month[i][6].replace("package=",""))
            data.append(collect_month[i][7].replace("totalTimeUsed=", "").replace('"',''))
            data.append(dateTime)
            data.append(collect_month[i][10].replace("totalTimeVisible=", "").replace('"',''))
            data.append(lastTime)
            new_month.append(data)

        new_df_month = pd.DataFrame(new_month, columns =['app_name', 'totalTimeUsed', 'lastTimeUsed', 'totalTimeVisible', 'lastTimeVisible'])
        dockercheck()
        print("monthly usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, monthly_doc_generator(new_df_month))

        #year csv
        print("yearly usagestats 파싱 중...")
        yearly_usage={}
        yearly_app_name=[] 
        yearly_totalTimeUsed=[] 
        yearly_lastTimeUsed=[]
        yearly_totalTimeVisible=[] 
        yearly_lastTimeVisible=[]
        for i in range(len(collect_year)):
            yearly_app_name.append(collect_year[i][6].replace("package=",""))
            yearly_totalTimeUsed.append(collect_year[i][7].replace("totalTimeUsed=", "").replace('"',''))
            yearly_lastTimeUsed.append("{} {}".format(collect_year[i][8].replace("lastTimeUsed=","").replace('"',''), collect_year[i][9]).replace('"',''))
            yearly_totalTimeVisible.append(collect_year[i][10].replace("totalTimeVisible=", "").replace('"',''))
            yearly_lastTimeVisible.append("{} {}".format(collect_year[i][11].replace("lastTimeVisible=","").replace('"',''), collect_year[i][12]).replace('"',''))

        yearly_usage['app_name']=yearly_app_name
        yearly_usage['totalTimeUsed']=yearly_totalTimeUsed
        yearly_usage['lastTimeUsed']=yearly_lastTimeUsed
        yearly_usage['totalTimeVisible']=yearly_totalTimeVisible
        yearly_usage['lastTimeVisible']=yearly_lastTimeVisible

        df_year=pd.DataFrame(yearly_usage)
        df_year.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_yearly_usagestats.csv".format(os.getcwd()))

        #elk 바로 업로드
        new_year=[]
        for i in range(len(collect_year)):
            data=[]
            string_last_time="{} {}".format(collect_year[i][8].replace("lastTimeUsed=","").replace('"',''), collect_year[i][9]).replace('"','')
            dateTime=datetime.strptime(string_last_time, datetime_format)
            string_visible_time="{} {}".format(collect_year[i][11].replace("lastTimeVisible=","").replace('"',''), collect_year[i][12]).replace('"','')
            lastTime=dateTime.strptime(string_visible_time, datetime_format)
            data.append(collect_year[i][6].replace("package=",""))
            data.append(collect_year[i][7].replace("totalTimeUsed=", "").replace('"',''))
            data.append(dateTime)
            data.append(collect_year[i][10].replace("totalTimeVisible=", "").replace('"',''))
            data.append(lastTime)
            new_year.append(data)

        new_df_year = pd.DataFrame(new_year, columns =['app_name', 'totalTimeUsed', 'lastTimeUsed', 'totalTimeVisible', 'lastTimeVisible'])
        dockercheck()
        print("yearly usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, yearly_doc_generator(new_df_year))
        
    if arge.woacc:
        createFolder("{}\\IWATCHU".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\extracted_files".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("1분 정도의 시간이 소요될 수 있습니다. 잠시만 기다려 주세요.")
            device1.shell("du | grep -v '/proc/'> sdcard/accesible_file_list.txt")
            device1.pull("sdcard/accesible_file_list.txt", "{}\\IWATCHU\\WearOS\\extracted_files\\accesible_file_list.txt".format(os.getcwd()))
            print("접근 가능 목록 추출이 완료되었습니다.")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("1분 정도의 시간이 소요될 수 있습니다. 잠시만 기다려 주세요.")
            device1.shell("du | grep -v '/proc/'> sdcard/accesible_file_list.txt")
            device1.pull("sdcard/accesible_file_list.txt", "{}\\IWATCHU\\WearOS\\extracted_files\\accesible_file_list.txt".format(os.getcwd()))
            print("접근 가능 목록 추출이 완료되었습니다.")

        f = open("{}\\IWATCHU\\WearOS\\extracted_files\\accesible_file_list.txt".format(os.getcwd()), "rt", encoding='UTF8')
        lines = f.readlines()

        accessible_files=[]

        for i in range(len(lines)):
            accessible_files.append(lines[i].replace("\n","").split("\t"))

        print(accessible_files)
        for z in range(len(accessible_files)):
            print("진행률 : {}/{}".format(z, len(accessible_files)))
            subprocess.call("adb pull {} {}\\IWATCHU\\WearOS\\extracted_files".format(accessible_files[z][1], os.getcwd(), shell=True))

        print("Accesible file list extraction complete")
        dockercheck()
        
    if arge.wopic:
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\synchronized_pictures".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\picture_location".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("Watch 내 jpg 파일 식별 중...")
            device1.shell("du -a | grep '.jpg' > data/local/tmp/pictures.txt")
            device1.pull("data/local/tmp/pictures.txt", "{}\\IWATCHU\\WearOS\\synchronized_pictures\\pictures.txt".format(os.getcwd()))

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("Watch 내 jpg 파일 식별 중...")
            device1.shell("du -a | grep '.jpg' > data/local/tmp/pictures.txt")
            device1.pull("data/local/tmp/pictures.txt", "{}\\IWATCHU\\WearOS\\synchronized_pictures\\pictures.txt".format(os.getcwd()))

        with open("{}\\IWATCHU\\WearOS\\synchronized_pictures\\pictures.txt".format(os.getcwd())) as f:
            lines = f.readlines()

        synchro_pictures=[]
        address_split=[]
        picture_name=[]

        for i in range(len(lines)):
            synchro_pictures.append(lines[i].replace("\n","").split("\t"))

        for i in range(len(synchro_pictures)):
            address_split.append(synchro_pictures[i][1].split("/"))

        for i in range(len(address_split)):
            for z in range(len(address_split[i])):
                if ".jpg" in address_split[i][z]:
                    picture_name.append(address_split[i][z])

        print("동기화된 사진 파일 추출 중...")
        for z in range(len(synchro_pictures)):
            device1.pull("{}".format(synchro_pictures[z][1]), "{}\\IWATCHU\\WearOS\\synchronized_pictures\\{}".format(os.getcwd(),picture_name[z]))

        print("동기화된 사진 파일 추출 완료")
        device1.shell("rm data/local/tmp/pictures.txt")

        gps_info=[]
        suspect_map=folium.Map(location=[36.63, 127.85], zoom_start=8) #우리나라 지도 위치(좌표 수정 안해도 됨.)

        for i in range(len(picture_name)):
            try:
                with open("{}\\IWATCHU\\WearOS\\synchronized_pictures\\{}".format(os.getcwd(),picture_name[i]), "rb") as picture:
                    img=Image(picture)
                    lati = ((img.gps_Latitude[2]/60)+img.gps_Latitude[1])/60+img.gps_Latitude[0]
                    longi = ((img.gps_Longitude[2]/60)+img.gps_Longitude[1])/60+img.gps_Longitude[0]
                    gps_info.append([lati, longi])

            except AttributeError:
                print("{}는 exif 정보가 없는 사진입니다.".format(picture_name[i]))

        for i in range(len(gps_info)):
            folium.Marker(location=[gps_info[i][0], gps_info[i][1]], icon=folium.Icon(color='red', icon='star', popup=str(picture_name[i]))).add_to(suspect_map)

        suspect_map.save("{}\\IWATCHU\\WearOS\\picture_location\\{}.html".format(os.getcwd(),picture_name[i]))
        url="{}\\IWATCHU\\WearOS\\picture_location\\{}.html".format(os.getcwd(),picture_name[i])
        webbrowser.open(url)
        print("Picture location information extraction complete")
        time.sleep(100) 
       
    if arge.wodel:
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\application".format(os.getcwd()))
        
        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]
            installed_packages=[]

            device1.shell("pm list packages > data/local/tmp/package_list.txt")
            device1.pull("data/local/tmp/package_list.txt", "{}\\IWATCHU\\WearOS\\application\\package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/package_list.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("pm list packages > data/local/tmp/package_list.txt")
            device1.pull("data/local/tmp/package_list.txt", "{}\\IWATCHU\\WearOS\\application\\package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/package_list.txt")


        current_packages=[]

        u=open("{}\\IWATCHU\\application\\package_list.txt".format(os.getcwd()),"r")
        current=u.readlines()
        for i in range(len(current)):
            current_packages.append(current[i].replace("package:","").replace("\n",""))

        device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
        device1.pull("sdcard/usagestats_result.txt", "{}\\IWATCHU\\WearOS\\application\\usagestats_result.txt".format(os.getcwd()))
        device1.shell("rm sdcard/usagestats_result.txt")

        f = open("{}\\IWATCHU\\WearOS\\application\\usagestats_result.txt".format(os.getcwd()), "r", encoding='utf-8')
        lines = f.readlines()
        ChooserCounts_num =0
        yearly_start=0
        yearly_end=0

        for i in range(len(lines)):
            if "In-memory yearly stats" in lines[i]:
                yearly_start=i
            if "ChooserCounts" in lines[i]:
                ChooserCounts_num += 1
                if ChooserCounts_num == 4:
                    yearly_end = i -2

        collect_year=[]
        for i in range(yearly_start, yearly_end+1):
            if "package=" in lines[i]:
                collect_year.append(lines[i].split(" "))

        year_packages=[]
        for i in range(len(collect_year)):
            year_packages.append(collect_year[i][6].replace("package=",""))

        deleted_packages=[]

        for i in range(len(year_packages)):
            if year_packages[i] not in current_packages:
                deleted_packages.append(year_packages[i])

        print("삭제된 애플리케이션 목록은 다음과 같습니다.")
        for i in range(len(deleted_packages)):
            print("{} {}".format(i+1, deleted_packages[i]))

        for i in range(len(deleted_packages)):
            url="https://play.google.com/store/apps/details?id={}".format(deleted_packages[i])
            webbrowser.open(url)

        time.sleep(100)    
    
    if arge.woall:
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\application".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\extracted_apk".format(os.getcwd()))
        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("설치된 apk 파일 확인 중...")
            device1.shell("pm list packages -f > data/local/tmp/installed_apk_list.txt")
            device1.pull("data/local/tmp/installed_apk_list.txt", "{}\\IWATCHU\\WearOS\\application\\installed_apk_list.txt".format(os.getcwd()))

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("설치된 apk 파일 확인 중...")
            device1.shell("pm list packages -f > data/local/tmp/installed_apk_list.txt")
            device1.pull("data/local/tmp/installed_apk_list.txt", "{}\\IWATCHU\\WearOS\\application\\installed_apk_list.txt".format(os.getcwd()))

        with open("{}\\IWATCHU\\WearOS\\application\\installed_apk_list.txt".format(os.getcwd())) as f:
            lines = f.readlines()

        installed_packages=[]

        for i in range(len(lines)):
            installed_packages.append(lines[i].replace("package:","").replace("\n","").split("apk"))

        #permission denied 발생 이유는 복사하려는 기존 파일이 복사해서 들어올 때 파일 명을 안정해줘서 그런거임.
        print("설치된 apk 파일 추출 중...")
        for z in range(len(installed_packages)):
            createFolder("{}/IWATCHU/extracted_apk/{}".format(os.getcwd(),installed_packages[z][1]))
            device1.pull("/{}apk".format(installed_packages[z][0]), "{}/IWATCHU/extracted_apk/{}/base.apk".format(os.getcwd(),installed_packages[z][1]))

        print("설치된 apk 파일 추출 완료")
        device1.shell("rm data/local/tmp/installed_apk_list.txt")        

        
        def netstats_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_netstats',
                    "_type"  : "_doc",
                    "_source" : document
                }
        
        es_client = connections.create_connection(hosts=['elastic:changeme@127.0.0.1:9200'])
        datetime_format="%Y-%m-%d %H:%M:%S"
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\netstats\\".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("dumpsys netstats | grep -v 'iface' > sdcard/network_list.txt")
            device1.pull("sdcard/network_list.txt", "{}\\IWATCHU\\WearOS\\netstats\\network_list.txt".format(os.getcwd()))
            device1.shell("rm sdcard/network_list.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("dumpsys netstats | grep -v 'iface' > sdcard/network_list.txt")
            device1.pull("sdcard/network_list.txt", "{}\\IWATCHU\\WearOS\\netstats\\network_list.txt".format(os.getcwd()))
            device1.shell("rm sdcard/network_list.txt")

        p = open("{}\\IWATCHU\\WearOS\\netstats\\network_list.txt".format(os.getcwd()), "r", encoding='utf-8')
        f = open("{}\\IWATCHU\\WearOS\\netstats\\network_info.txt".format(os.getcwd()), "a", encoding='utf-8')

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


        #csv로 출력하기
        netstats={}
        networkId_array=[]
        connected_datetime=[]
        connected_timestamp=[]
        download_byte=[]
        download_packet=[]
        upload_byte=[]
        upload_packet=[]
        for i in range(len(modify)):
            if 'networkId' in modify[i]:
                networkId=str(modify[i].replace(' networkId=',"").replace('\"',"").replace('<',"").replace('>',""))
            else:
                networkId_array.append(networkId)
                connected_datetime.append(str(datetime.fromtimestamp(modify[i][0])))
                connected_timestamp.append(str(modify[i][0]))
                download_byte.append(str(modify[i][1]))
                download_packet.append(str(modify[i][2]))
                upload_byte.append(str(modify[i][3]))
                upload_packet.append(str(modify[i][4]))

        netstats['networkId']=networkId_array
        netstats['connected_datetime']=connected_datetime
        netstats['connected_timestamp']=connected_timestamp
        netstats['download_byte']=download_byte
        netstats['download_packet']=download_packet
        netstats['upload_byte']=upload_byte
        netstats['upload_packet']=upload_packet

        df_net=pd.DataFrame(netstats)
        df_net.to_csv("{}\\IWATCHU\\WearOS\\netstats\\fin_netstats.csv".format(os.getcwd()))

        new_netstats=[]
        for i in range(len(modify)):
            if 'networkId' in modify[i]:
                networkId=str(modify[i].replace(' networkId=',"").replace('\"',"").replace('<',"").replace('>',""))
            else:
                data=[networkId, datetime.fromtimestamp(modify[i][0]), modify[i][0], modify[i][1], modify[i][2], modify[i][3], modify[i][4]]
                new_netstats.append(data)

        elk_netstats = pd.DataFrame(new_netstats, columns =['networkId', 'connected_datetime', 'connected_timestamp', 'download_byte', 'download_packet', 'upload_byte', 'uploda_packet'])
        dockercheck()
        print("netstats elk 서버 전송 중...")
        helpers.bulk(es_client, netstats_generator(elk_netstats))
        
        def app_info_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_3rd_application_info',
                    "_type"  : "_doc",
                    "_source" : document
                }
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\application".format(os.getcwd()))

        es_client = connections.create_connection(hosts=['elastic:changeme@127.0.0.1:9200'])
        datetime_format="%Y-%m-%d %H:%M:%S"

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]
            installed_packages=[]

            device1.shell("pm list packages -3 > data/local/tmp/3rd_package_list.txt")
            device1.pull("data/local/tmp/3rd_package_list.txt", "{}\\IWATCHU\\WearOS\\application\\3rd_package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/3rd_package_list.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("pm list packages -3 > data/local/tmp/3rd_package_list.txt")
            device1.pull("data/local/tmp/3rd_package_list.txt", "{}\\IWATCHU\\WearOS\\application\\3rd_package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/3rd_package_list.txt")

        p=open("{}\\IWATCHU\\WearOS\\application\\3rd_package_list.txt".format(os.getcwd()), "r")

        lines = p.readlines()

        package_info=[]
        firstInstallLine=0
        req_perm_start=0
        req_perm_end=0
        install_time=[]
        for i in range(len(lines)):
            app_name=lines[i].replace("package:", "").replace("\n","")
            device1.shell("dumpsys package {} > data/local/tmp/{}_dumpsys.txt".format(app_name, app_name))
            device1.pull("data/local/tmp/{}_dumpsys.txt".format(app_name),  "{}\\IWATCHU\\WearOS\\WearOS\\application\\{}_dumpsys.txt".format(os.getcwd(), app_name))
            device1.shell("rm dumpsys package {}".format(app_name, app_name))
            f=open("{}\\IWATCHU\\WearOS\\application\\{}_dumpsys.txt".format(os.getcwd(), app_name), "r")
            package_lines=f.readlines()
            for z in range(len(package_lines)):
                if "firstInstallTime" in package_lines[z]:
                    firstInstallLine=z
                    install_time.append(package_lines[firstInstallLine].split(" "))
                if "requested permissions:" in package_lines[z]:
                    req_perm_start=z+1
                if "install permissions:" in package_lines[z]:
                    req_perm_end=z
            
            for q in range(req_perm_start, req_perm_end):
                dateTime=datetime.strptime("{} {}".format(install_time[i][4].replace("firstInstallTime=",""), install_time[i][5].replace("\n","")), datetime_format)
                package_info.append([str(app_name), dateTime , str(package_lines[q].replace(" ","").replace("\n",""))])

        third_package_info = pd.DataFrame(package_info, columns =['app_name', 'firstInstallTime', 'requested permission'])
        dockercheck()
        print("서드파티 앱 정보 elk 서버 전송 중...")
        helpers.bulk(es_client, app_info_generator(third_package_info))
        
        def daily_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_daily_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }

        def weekly_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_weekly_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }

        def monthly_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_monthly_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }

        def yearly_doc_generator(df):
            df_iter = df.iterrows()
            for index, document in df_iter:
                yield {
                    "_index" : 'wear_os_yearly_usagestats',
                    "_type"  : "_doc",
                    "_source" : document
                }
                
        es_client = connections.create_connection(hosts=['elastic:changeme@127.0.0.1:9200'])
        datetime_format="%Y-%m-%d %H:%M:%S"
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\usagestats".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("잠시만 기다려 주세요.")
            device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
            device1.pull("sdcard/usagestats_result.txt", "{}\\IWATCHU\\WearOS\\usagestats\\usagestats_result.txt".format(os.getcwd()))
            device1.shell("rm sdcard/usagestats_result.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("잠시만 기다려 주세요. 네트워크 로그 수집 중...")
            device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
            device1.pull("sdcard/usagestats_result.txt", "{}\\IWATCHU\\WearOS\\usagestats\\usagestats_result.txt".format(os.getcwd()))
            device1.shell("rm sdcard/usagestats_result.txt")
        
        f = open("{}\\IWATCHU\\WearOS\\usagestats\\usagestats_result.txt".format(os.getcwd()), "r", encoding='utf-8')
        lines = f.readlines()


        #24시간 usagestats
        collect_24h = []

        for i in range(len(lines)):
            if "time=" in lines[i]:
                collect_24h.append(lines[i].split(" "))

        daily_usage={}
        daily_datetime=[]
        daily_timestamp=[]
        daily_status=[]
        daily_appname=[]

        #daily usagestats csv
        print("daily usagestats 파싱 중...")
        for i in range(len(collect_24h)):
            stringtime="{} {}".format(str(collect_24h[i][4]).replace('time="', ''), str(collect_24h[i][5]).replace('"',''))
            daily_datetime.append(stringtime)
            daily_timestamp.append("{}".format(time.mktime(datetime.strptime(stringtime, '%Y-%m-%d %H:%M:%S').timetuple())))
            daily_status.append(collect_24h[i][6].replace("type=",""))
            daily_appname.append(collect_24h[i][7].replace("package=", ""))

        daily_usage['datetime']=daily_datetime
        daily_usage['timestamp']=daily_timestamp
        daily_usage['status']=daily_status
        daily_usage['appname']=daily_appname

        df_day=pd.DataFrame(daily_usage)
        df_day.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_daily_usagestats.csv".format(os.getcwd()))

        #daily usagestats elk
        new_day=[]
        for i in range(len(collect_24h)):
            data=[]
            stringtime="{} {}".format(str(collect_24h[i][4]).replace('time="', ''), str(collect_24h[i][5]).replace('"',''))
            toDateTime=datetime.strptime(stringtime, datetime_format)
            data.append(toDateTime)
            data.append(collect_24h[i][7].replace("package=", ""))
            data.append("{}".format(time.mktime(datetime.strptime(stringtime, '%Y-%m-%d %H:%M:%S').timetuple())))
            data.append(collect_24h[i][6].replace("type=",""))
            new_day.append(data)

        new_df_day = pd.DataFrame(new_day, columns =['datetime', 'app_name', 'timestamp', 'status'])
        dockercheck()
        print("daily usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, daily_doc_generator(new_df_day))

        #주, 월, 년 별 사용 내역이 담긴 열의 범위 확인
        ChooserCounts_num =0
        weekly_start=0
        weekly_end=0

        monthly_start=0
        monthly_end=0

        yearly_start=0
        yearly_end=0

        for i in range(len(lines)):
            if "In-memory weekly stats" in lines[i]:
                weekly_start=i
            if "In-memory monthly stats" in lines[i]:
                monthly_start=i
            if "In-memory yearly stats" in lines[i]:
                yearly_start=i
            if "ChooserCounts" in lines[i]:
                ChooserCounts_num += 1
                if ChooserCounts_num == 2:
                    weekly_end = i - 2
                if ChooserCounts_num == 3:
                    monthly_end = i -2
                if ChooserCounts_num == 4:
                    yearly_end = i -2
                
        #주, 월, 년 별 범위를 각각의 리스트에 저장
        collect_week=[]
        collect_month=[]
        collect_year=[]

        for i in range(weekly_start, weekly_end+1):
            if "package=" in lines[i]:
                collect_week.append(lines[i].split(" "))

        for i in range(monthly_start, monthly_end+1):
            if "package=" in lines[i]:
                collect_month.append(lines[i].split(" "))

        for i in range(yearly_start, yearly_end+1):
            if "package=" in lines[i]:
                collect_year.append(lines[i].split(" "))

        #print(lines[weekly_start])
        #print(collect_week[0])
        #print(collect_month[0])
        #print(collect_year[0])

        #week csv
        print("weekly usagestats 파싱 중...")
        weekly_usage={}
        weekly_app_name=[] 
        weekly_totalTimeUsed =[]
        weekly_lastTimeUsed=[] 
        weekly_totalTimeVisible=[] 
        weekly_lastTimeVisible=[]
        for i in range(len(collect_week)):
            weekly_app_name.append(collect_week[i][6].replace("package=",""))
            weekly_totalTimeUsed.append(collect_week[i][7].replace("totalTimeUsed=", "").replace('"',''))
            weekly_lastTimeUsed.append("{} {}".format(collect_week[i][8].replace("lastTimeUsed=","").replace('"',''), collect_week[i][9]).replace('"',''))
            weekly_totalTimeVisible.append(collect_week[i][10].replace("totalTimeVisible=", "").replace('"',''))
            weekly_lastTimeVisible.append("{} {}".format(collect_week[i][11].replace("lastTimeVisible=","").replace('"',''), collect_week[i][12]).replace('"',''))

        weekly_usage['app_name']=weekly_app_name
        weekly_usage['totalTimeUsed']=weekly_totalTimeUsed
        weekly_usage['lastTimeUsed']=weekly_lastTimeUsed
        weekly_usage['totalTimeVisible']=weekly_totalTimeVisible
        weekly_usage['lastTimeVisible']=weekly_lastTimeVisible

        df_week=pd.DataFrame(weekly_usage)
        df_week.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_weekly_usagestats.csv".format(os.getcwd()))

        #elk 바로 업로드
        new_week=[]
        for i in range(len(collect_week)):
            string_last_time="{} {}".format(collect_week[i][8].replace("lastTimeUsed=","").replace('"',''), collect_week[i][9]).replace('"','')
            dateTime=datetime.strptime(string_last_time, datetime_format)
            string_visible_time="{} {}".format(collect_week[i][11].replace("lastTimeVisible=","").replace('"',''), collect_week[i][12]).replace('"','')
            lastTime=dateTime.strptime(string_visible_time, datetime_format)
            data=[]
            data.append(collect_week[i][6].replace("package=",""))
            data.append(collect_week[i][7].replace("totalTimeUsed=", "").replace('"',''))
            data.append(dateTime)
            data.append(collect_week[i][10].replace("totalTimeVisible=", "").replace('"',''))
            data.append(lastTime)
            new_week.append(data)

        new_df_week = pd.DataFrame(new_week, columns =['app_name', 'totalTimeUsed', 'lastTimeUsed', 'totalTimeVisible', 'lastTimeVisible'])
        dockercheck()
        print("weekly usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, weekly_doc_generator(new_df_week))

        #month csv
        print("monthly usagestats 파싱 중...")
        monthly_usage={}
        monthly_app_name=[]
        monthly_totalTimeUsed=[]
        monthly_lastTimeUsed=[]
        monthly_totalTimeVisible=[]
        monthly_lastTimeVisible=[]
        for i in range(len(collect_month)):
            monthly_app_name.append(collect_month[i][6].replace("package=",""))
            monthly_totalTimeUsed.append(collect_month[i][7].replace("totalTimeUsed=", "").replace('"',''))
            monthly_lastTimeUsed.append("{} {}".format(collect_month[i][8].replace("lastTimeUsed=","").replace('"',''), collect_month[i][9]).replace('"',''))
            monthly_totalTimeVisible.append(collect_month[i][10].replace("totalTimeVisible=", "").replace('"',''))
            monthly_lastTimeVisible.append("{} {}".format(collect_month[i][11].replace("lastTimeVisible=","").replace('"',''), collect_month[i][12]).replace('"',''))

        monthly_usage['app_name']=monthly_app_name
        monthly_usage['totalTimeUsed']=monthly_totalTimeUsed
        monthly_usage['lastTimeUsed']=monthly_lastTimeUsed
        monthly_usage['totalTimeVisible']=monthly_totalTimeVisible
        monthly_usage['lastTimeVisible']=monthly_lastTimeVisible

        df_month=pd.DataFrame(monthly_usage)
        df_month.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_monthly_usagestats.csv".format(os.getcwd()))

        #elk 바로 업로드
        new_month=[]
        for i in range(len(collect_month)):
            data=[]
            string_last_time="{} {}".format(collect_month[i][8].replace("lastTimeUsed=","").replace('"',''), collect_month[i][9]).replace('"','')
            dateTime=datetime.strptime(string_last_time, datetime_format)
            string_visible_time="{} {}".format(collect_month[i][11].replace("lastTimeVisible=","").replace('"',''), collect_month[i][12]).replace('"','')
            lastTime=dateTime.strptime(string_visible_time, datetime_format)
            data.append(collect_month[i][6].replace("package=",""))
            data.append(collect_month[i][7].replace("totalTimeUsed=", "").replace('"',''))
            data.append(dateTime)
            data.append(collect_month[i][10].replace("totalTimeVisible=", "").replace('"',''))
            data.append(lastTime)
            new_month.append(data)

        new_df_month = pd.DataFrame(new_month, columns =['app_name', 'totalTimeUsed', 'lastTimeUsed', 'totalTimeVisible', 'lastTimeVisible'])
        dockercheck()
        print("monthly usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, monthly_doc_generator(new_df_month))

        #year csv
        print("yearly usagestats 파싱 중...")
        yearly_usage={}
        yearly_app_name=[] 
        yearly_totalTimeUsed=[] 
        yearly_lastTimeUsed=[]
        yearly_totalTimeVisible=[] 
        yearly_lastTimeVisible=[]
        for i in range(len(collect_year)):
            yearly_app_name.append(collect_year[i][6].replace("package=",""))
            yearly_totalTimeUsed.append(collect_year[i][7].replace("totalTimeUsed=", "").replace('"',''))
            yearly_lastTimeUsed.append("{} {}".format(collect_year[i][8].replace("lastTimeUsed=","").replace('"',''), collect_year[i][9]).replace('"',''))
            yearly_totalTimeVisible.append(collect_year[i][10].replace("totalTimeVisible=", "").replace('"',''))
            yearly_lastTimeVisible.append("{} {}".format(collect_year[i][11].replace("lastTimeVisible=","").replace('"',''), collect_year[i][12]).replace('"',''))

        yearly_usage['app_name']=yearly_app_name
        yearly_usage['totalTimeUsed']=yearly_totalTimeUsed
        yearly_usage['lastTimeUsed']=yearly_lastTimeUsed
        yearly_usage['totalTimeVisible']=yearly_totalTimeVisible
        yearly_usage['lastTimeVisible']=yearly_lastTimeVisible

        df_year=pd.DataFrame(yearly_usage)
        df_year.to_csv("{}\\IWATCHU\\WearOS\\usagestats\\fin_yearly_usagestats.csv".format(os.getcwd()))

        #elk 바로 업로드
        new_year=[]
        for i in range(len(collect_year)):
            data=[]
            string_last_time="{} {}".format(collect_year[i][8].replace("lastTimeUsed=","").replace('"',''), collect_year[i][9]).replace('"','')
            dateTime=datetime.strptime(string_last_time, datetime_format)
            string_visible_time="{} {}".format(collect_year[i][11].replace("lastTimeVisible=","").replace('"',''), collect_year[i][12]).replace('"','')
            lastTime=dateTime.strptime(string_visible_time, datetime_format)
            data.append(collect_year[i][6].replace("package=",""))
            data.append(collect_year[i][7].replace("totalTimeUsed=", "").replace('"',''))
            data.append(dateTime)
            data.append(collect_year[i][10].replace("totalTimeVisible=", "").replace('"',''))
            data.append(lastTime)
            new_year.append(data)

        new_df_year = pd.DataFrame(new_year, columns =['app_name', 'totalTimeUsed', 'lastTimeUsed', 'totalTimeVisible', 'lastTimeVisible'])
        dockercheck()
        print("yearly usagestats elk 서버 전송 중...")
        helpers.bulk(es_client, yearly_doc_generator(new_df_year))
        
        createFolder("{}\\IWATCHU".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\extracted_files".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("1분 정도의 시간이 소요될 수 있습니다. 잠시만 기다려 주세요.")
            device1.shell("du | grep -v '/proc/'> sdcard/accesible_file_list.txt")
            device1.pull("sdcard/accesible_file_list.txt", "{}\\IWATCHU\\WearOS\\extracted_files\\accesible_file_list.txt".format(os.getcwd()))
            print("접근 가능 목록 추출이 완료되었습니다.")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("1분 정도의 시간이 소요될 수 있습니다. 잠시만 기다려 주세요.")
            device1.shell("du | grep -v '/proc/'> sdcard/accesible_file_list.txt")
            device1.pull("sdcard/accesible_file_list.txt", "{}\\IWATCHU\\WearOS\\extracted_files\\accesible_file_list.txt".format(os.getcwd()))
            print("접근 가능 목록 추출이 완료되었습니다.")

        f = open("{}\\IWATCHU\\WearOS\\extracted_files\\accesible_file_list.txt".format(os.getcwd()), "rt", encoding='UTF8')
        lines = f.readlines()

        accessible_files=[]

        for i in range(len(lines)):
            accessible_files.append(lines[i].replace("\n","").split("\t"))

        print(accessible_files)
        for z in range(len(accessible_files)):
            print("진행률 : {}/{}".format(z, len(accessible_files)))
            subprocess.call("adb pull {} {}\\IWATCHU\\WearOS\\extracted_files".format(accessible_files[z][1], os.getcwd(), shell=True))

        print("Accesible file list extraction complete")
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\synchronized_pictures".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\picture_location".format(os.getcwd()))

        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("Watch 내 jpg 파일 식별 중...")
            device1.shell("du -a | grep '.jpg' > data/local/tmp/pictures.txt")
            device1.pull("data/local/tmp/pictures.txt", "{}\\IWATCHU\\WearOS\\synchronized_pictures\\pictures.txt".format(os.getcwd()))

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            print("Watch 내 jpg 파일 식별 중...")
            device1.shell("du -a | grep '.jpg' > data/local/tmp/pictures.txt")
            device1.pull("data/local/tmp/pictures.txt", "{}\\IWATCHU\\WearOS\\synchronized_pictures\\pictures.txt".format(os.getcwd()))

        with open("{}\\IWATCHU\\WearOS\\synchronized_pictures\\pictures.txt".format(os.getcwd())) as f:
            lines = f.readlines()

        synchro_pictures=[]
        address_split=[]
        picture_name=[]

        for i in range(len(lines)):
            synchro_pictures.append(lines[i].replace("\n","").split("\t"))

        for i in range(len(synchro_pictures)):
            address_split.append(synchro_pictures[i][1].split("/"))

        for i in range(len(address_split)):
            for z in range(len(address_split[i])):
                if ".jpg" in address_split[i][z]:
                    picture_name.append(address_split[i][z])

        print("동기화된 사진 파일 추출 중...")
        for z in range(len(synchro_pictures)):
            device1.pull("{}".format(synchro_pictures[z][1]), "{}\\IWATCHU\\WearOS\\synchronized_pictures\\{}".format(os.getcwd(),picture_name[z]))

        print("동기화된 사진 파일 추출 완료")
        device1.shell("rm data/local/tmp/pictures.txt")

        gps_info=[]
        suspect_map=folium.Map(location=[36.63, 127.85], zoom_start=8) #우리나라 지도 위치(좌표 수정 안해도 됨.)

        for i in range(len(picture_name)):
            try:
                with open("{}\\IWATCHU\\WearOS\\synchronized_pictures\\{}".format(os.getcwd(),picture_name[i]), "rb") as picture:
                    img=Image(picture)
                    lati = ((img.gps_Latitude[2]/60)+img.gps_Latitude[1])/60+img.gps_Latitude[0]
                    longi = ((img.gps_Longitude[2]/60)+img.gps_Longitude[1])/60+img.gps_Longitude[0]
                    gps_info.append([lati, longi])

            except AttributeError:
                print("{}는 exif 정보가 없는 사진입니다.".format(picture_name[i]))

        for i in range(len(gps_info)):
            folium.Marker(location=[gps_info[i][0], gps_info[i][1]], icon=folium.Icon(color='red', icon='star', popup=str(picture_name[i]))).add_to(suspect_map)

        suspect_map.save("{}\\IWATCHU\\WearOS\\picture_location\\{}.html".format(os.getcwd(),picture_name[i]))
        url="{}\\IWATCHU\\WearOS\\picture_location\\{}.html".format(os.getcwd(),picture_name[i])
        webbrowser.open(url)
        print("Picture location information extraction complete")
        time.sleep(100)
        
        createFolder("{}\\IWATCHU\\".format(os.getcwd()))
        createFolder("{}\\IWATCHU\\WearOS\\application".format(os.getcwd()))
        
        try:
            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]
            installed_packages=[]

            device1.shell("pm list packages > data/local/tmp/package_list.txt")
            device1.pull("data/local/tmp/package_list.txt", "{}\\IWATCHU\\WearOS\\application\\package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/package_list.txt")

        except :
            print("스마트워치와의 연결 상태가 불량합니다.\n워치를 재부팅하고 데스크탑과 동일한 네트워크에 연결한 후 디버깅을 허가해주십시오.")
            watch_ip=input("스마트워치의 IP와 Port 값을 입력하십시오: ")
            subprocess.call("{}\\adb.exe connect {}".format(os.getcwd(), watch_ip), shell=True)
            print("스마트워치 화면에서 디버깅을 승인해주십시오.")

            time.sleep(10)

            client = AdbClient(host='127.0.0.1', port=5037)
            devices = client.devices()
            device1 = devices[0]

            device1.shell("pm list packages > data/local/tmp/package_list.txt")
            device1.pull("data/local/tmp/package_list.txt", "{}\\IWATCHU\\WearOS\\application\\package_list.txt".format(os.getcwd()))
            device1.shell("rm data/local/tmp/package_list.txt")


        current_packages=[]

        u=open("{}\\IWATCHU\\application\\package_list.txt".format(os.getcwd()),"r")
        current=u.readlines()
        for i in range(len(current)):
            current_packages.append(current[i].replace("package:","").replace("\n",""))

        device1.shell("dumpsys usagestats > sdcard/usagestats_result.txt")
        device1.pull("sdcard/usagestats_result.txt", "{}\\IWATCHU\\WearOS\\application\\usagestats_result.txt".format(os.getcwd()))
        device1.shell("rm sdcard/usagestats_result.txt")

        f = open("{}\\IWATCHU\\WearOS\\application\\usagestats_result.txt".format(os.getcwd()), "r", encoding='utf-8')
        lines = f.readlines()
        ChooserCounts_num =0
        yearly_start=0
        yearly_end=0

        for i in range(len(lines)):
            if "In-memory yearly stats" in lines[i]:
                yearly_start=i
            if "ChooserCounts" in lines[i]:
                ChooserCounts_num += 1
                if ChooserCounts_num == 4:
                    yearly_end = i -2

        collect_year=[]
        for i in range(yearly_start, yearly_end+1):
            if "package=" in lines[i]:
                collect_year.append(lines[i].split(" "))

        year_packages=[]
        for i in range(len(collect_year)):
            year_packages.append(collect_year[i][6].replace("package=",""))

        deleted_packages=[]

        for i in range(len(year_packages)):
            if year_packages[i] not in current_packages:
                deleted_packages.append(year_packages[i])

        print("삭제된 애플리케이션 목록은 다음과 같습니다.")
        for i in range(len(deleted_packages)):
            print("{} {}".format(i+1, deleted_packages[i]))

        for i in range(len(deleted_packages)):
            url="https://play.google.com/store/apps/details?id={}".format(deleted_packages[i])
            webbrowser.open(url)

        time.sleep(100)
        