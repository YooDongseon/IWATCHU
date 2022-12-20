import argparse
import os
from datetime import datetime
import json 
import subprocess
import pandas as pd
import re
import sys
import tempfile
import tarfile
from matplotlib import pyplot as plt

def main(path):                                                                                                                                # Tizen OS App level 메인
    
    print(path)
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
                docker_name = c[i + 2]
                if docker_name[1:11] != "docker-elk":
                    sys.exit()
            
        except:
            print("Check your docker environment")
            sys.exit()
    
    Select2 = argparse.ArgumentParser(description='Smart Watch analyzer for Tizen OS in application level')
    
    result_path_defalut = "{}\\IWATCHU\\".format(os.getcwd())
    Select2.add_argument("Tizen", metavar='N', action='store')
    Select2.add_argument("app", metavar='N', action='store')
    Select2.add_argument('path', type = str, action='store')  
    Select2.add_argument("--csc", dest="csc", action='store_true', help="At Tizen os in application level, get CSC version and region code")  
    Select2.add_argument("--swc", dest="swc", action='store_true', help="At Tizen os in application level, get country code of software released")
    Select2.add_argument("--vconf", dest="vconf", action='store_true', help="At Tizen os in application level, get a setting of companion which connected to watch") 
    Select2.add_argument("--gps", dest="gps", action='store_true', help="At Tizen os in application level, get parse gps data and show path in jpg. And upload json output to elk-stack")
    Select2.add_argument("--reboot", dest="reboot", action='store_true', help="At Tizen os in application level, get a rebooting log. And upload json output to elk-stack")
    Select2.add_argument("--time", dest="time", action='store_true', help="At Tizen os in application level, get information of time. And upload json output to elk-stack")
    Select2.add_argument("--battery", dest="battery", action='store_true', help="At Tizen os in application level, get information of battery usage and show graph as jpg. And upload json output to elk-stack")
    Select2.add_argument("--res", dest="res", action='store_true', help="At Tizen os in application level, get information of resources. And upload json output to elk-stack")
    Select2.add_argument("--appuse", dest="appuse", action='store_true', help="At Tizen os in application level, get log of application usage. And upload json output to elk-stack")
    Select2.add_argument("--appinst", dest="appinst", action='store_true', help="At Tizen os in application level, get log of application install. And upload json output to elk-stack")
    Select2.add_argument("--bootcnt", dest="bootcount", action='store_true', help="At Tizen os in application level, get log of application install")
    Select2.add_argument("--all", dest="all", action='store_true', help="At Tizen os in application level, get a all information of above. And upload json outputs to elk-stack")
    arge = Select2.parse_args()
    
    AppInputDir = path
    AppOutputDir=result_path_defalut + "\\TizenOS\\Application level"
    AppOutputDirMod=AppOutputDir+'\\Module_log'
    AppOutputVar=AppOutputDir+'\\Var_log'
    os.makedirs(AppOutputDir, exist_ok=True)
    os.makedirs(AppOutputDirMod, exist_ok=True)
    os.makedirs(AppOutputVar, exist_ok=True)
    
    if arge.csc:
        CSCV=re.compile(r'CSC Version : ([0-9A-Z]{12})')
        CSCC=re.compile(r'Sales code : ([A-Z]{3})')
        FileDir=AppInputDir+"\\module_log\\csc\\csc-default\\output\\csc-verification-report.log"
        with open(FileDir, 'r') as f:
            k=f.read()
        CSC_Version=str(CSCV.findall(k)[0])
        Region_code=str(CSCC.findall(k)[0])

        with open(AppOutputDirMod+'\\1_CSCversion.json', 'w') as fp:
            json.dump({'CSC_Version':CSC_Version, 'Region_code':Region_code}, fp)
        print({'CSC_Version':CSC_Version, 'Region_code':Region_code})
    
    if arge.swc:
        SWC=re.compile(r'/([A-Z]{3})/')
        FileDir=AppInputDir+"\\module_log\\csc\\csc-default\\SW_Configuration.xml"
        with open(FileDir, 'r', encoding="utf-8") as f:
            k=f.read()
        SWCall=SWC.findall(k)
        print("Available Sales Number : ", len(SWCall))
        with open(AppOutputDirMod+'\\2_CSCCode.json', 'w') as fp:
            json.dump({'Available Sales Code':SWCall}, fp)
            
    if arge.vconf:
        vconfr=re.compile(r'value = (\d+)')
        FileDir=AppInputDir+"\\module_log\\gps\\vconf"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        dic={}
        for t in k:
            print(t[:-1])
            dic[t.split(',')[0]]=vconfr.findall(t.split(',')[1])[0]
        with open(AppOutputDirMod+'\\3_Vconf.json', 'w') as fp:
            json.dump(dic, fp)
            
    if arge.gps:
        AppStartInfoR=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} START .*')
        AppStopInfoR=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} STOP .*')
        AppGPSInfoR=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} .* pos -> .* \[.*\] - \[.*\]')
        AppGPSInfoR2=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} .* pos -> .* \[.*\] - \[([\dx]*) : ([\dx]*)\]')
        FileDir=AppInputDir+"\\module_log\\gps\\location.tar.gz"
        with tempfile.TemporaryDirectory() as tmpdir:
            file=tarfile.open(FileDir)
            file.extractall(tmpdir)
            file.close()
            print(os.listdir(tmpdir))
            for file in os.listdir(tmpdir):
                time=[]
                x=[]
                y=[]
                x_accum=[]
                y_accum=[]
                if "dump_gps" in file:
                    with open(tmpdir+"\\"+file, 'r') as f:
                        k=f.read()
                        AppStartInfo=AppStartInfoR.findall(k)
                        AppStopInfo=AppStopInfoR.findall(k)
                        AppGPSInfo=AppGPSInfoR.findall(k)
                    Appstartlist=[]
                    Appstartdict={}
                    for i in AppStartInfo:
                        #10/26 11:17:52.821 START COMPANION-WPS from [lbs-server/get_ref_location]
                        strs=i.split('START')
                        Appstartdict['Time']=strs[0]
                        Appstartdict['Info']=(strs[1]).split('from')[0]
                        Appstartdict['Service']=((strs[1]).split('from')[1])[1:]
                        Appstartlist.append(Appstartdict)
                    Appstoplist=[]
                    Appstopdict={}
                    for i in AppStopInfo:
                        strs=i.split('STOP')
                        Appstopdict['Time']=strs[0]
                        Appstopdict['Info']=(strs[1]).split('from')[0]
                        Appstopdict['Service']=((strs[1]).split('from')[1])[1:]
                        Appstoplist.append(Appstopdict)
                        print(Appstopdict)
                        print(i)
                    Sensorinfo=[]
                    num=[]
                    x_real=[]
                    y_real=[]
                    for i in AppGPSInfo:
                        time.append(datetime.strptime(i[:18], "%m/%d %H:%M:%S.%f"))
                        #[3x.4x6x0x : 1x7.x3x5x1]
                        #x.append(i[-23:-15])
                        #y.append(i[-20:-3])
                        #11/06 10:36:28.416 companion-wps pos -> FW : [0] - [3x.4x6x0x : 1x7.x3x5x4]
                        x.append(int(i[-16]))
                        y.append(int(i[-4]))
                        x_real.append(i[-23:-14])
                        y_real.append(i[-11:-1])
                        Sensorinfo.append(i.split(' ')[2])
                        num.append(i.split(' ')[7][1:-1])
                    x_accum.append(x[0])
                    y_accum.append(y[0])
                    for i in range(len(x)-1):
                        x_accum.append(x_accum[i])
                        if (x[i+1]-(x_accum[i]%10)+10)%10<=5:
                            while x_accum[i+1]%10!=x[i+1]:
                                x_accum[i+1]=x_accum[i+1]+1
                        else:
                            while x_accum[i+1]%10!=x[i+1]:
                                x_accum[i+1]=x_accum[i+1]-1
                        y_accum.append(y_accum[i])
                        if (y[i+1]-(y_accum[i]%10)+10)%10<=5:
                            while y_accum[i+1]%10!=y[i+1]:
                                y_accum[i+1]=y_accum[i+1]+1
                        else:
                            while y_accum[i+1]%10!=y[i+1]:
                                y_accum[i+1]=y_accum[i+1]-1
                    for i in range(len(y_accum)):
                        y_accum[i]=y_accum[i]*10
                        #print(x[i]/10, y[i], x_accum[i]/10, y_accum[i])
                    
                    df=pd.DataFrame({'Date':[datetime.strftime(x, "%m.%d %H:%M:%S.%f") for x in time],'Sensorinfo':Sensorinfo, 'num':num, 'X':x_real, 'Y':y_real, 'X_accum':x_accum, 'Y_accum':y_accum})
                    plt.figure(figsize=((max(y_accum)-min(y_accum))/200,(max(x_accum)-min(x_accum))/200))
                    #plt.plot(y_accum, x_accum,color='skyblue',marker='o', markerfacecolor='blue',markersize=6)
                    #1틱: 대략 11.1미터, 곧 초속 50미터 이하의 범위에서는 (시속 200km 이하) 유효할 것으로 예상
                    plt.axis('off')
                    plt.title(file)
                    plt.plot(y_accum, x_accum,'bo', markersize=3)
                    plt.savefig(AppOutputDirMod+f'\\4_2_locationIMG_{file}.jpg')
                    
                    dic={'START':Appstartlist, 'STOP':Appstoplist}
                    with open(AppOutputDirMod+f'\\4_1_locationSTARTSTOP_{file}.json', 'w') as fp:
                        json.dump(dic, fp)
                    df.to_json(AppOutputDirMod+f'\\4_2_locationDUMP_{file}.json', orient='records')
                else:
                    pass
        dockercheck() 
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + f'\\4_2_locationDUMP_{file}.json' + "-A 'gpslog'"
        subprocess.check_output(elastic_query)
        
    if arge.reboot:
        FileDir=AppInputDir+"\\module_log\\power\\pm_reset_log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        di={}
        di['LOGTIME']=k[0][:-1]
        lis={}
        for i in k[2:]:
            if i=='\n': break
            lis[i[:24]]=i.split(' ')[-1][:-1]
        di['LOG']=lis
        with open(AppOutputDirMod+'\\5_pm_reset_log.json', 'w') as fp:
            json.dump(di, fp)
            
        dockercheck()    
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\5_pm_reset_log.json' + "-A 'rebootlog'"
        subprocess.check_output(elastic_query)
        
    if arge.time:
        systemtimeR=re.compile(r'system time : (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \(.*\)')
        timezoneR=re.compile(r'timezone\s+: .* \(.*\)')
        FileDir=AppInputDir+"\\module_log\\power\\pm_time_history"
        with open(FileDir, 'r') as f:
            k=f.read()
        txt=k.split('\n\n')
        timehistoryheader={}
        for l in txt[2].split('\n'):
            timehistoryheader[l.split(':')[0].strip(' ')]=(':'.join( l.split(':')[1:])).strip(' ')
            
        timelogheader=re.split(r'\s\s+', txt[3].split('\n')[0])[1:]
        df=pd.DataFrame(columns=timelogheader)
        dividepoint=[21,28,44,50,65,83,107,129,141]
        for line in txt[3].split('\n')[1:]:
            dat=[]
            st=0
            for p in dividepoint:
                dat.append(line[st:p-1].strip()) 
                st=p-1
            dat.append(line[st:].strip())
            df=pd.concat([df, pd.DataFrame([dat], columns=timelogheader)], ignore_index=True)
        di={'Info':timehistoryheader}
        with open(AppOutputDirMod+'\\6_1_pm_time_history_LOGINFO.json', 'w') as fp:
            json.dump(di, fp)
        df.to_json(AppOutputDirMod+'\\6_2_pm_time_history_LOG.json', orient='records')
        
        dockercheck()
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\6_2_pm_time_history_LOG.json' + "-A 'timeinfo'"
        subprocess.check_output(elastic_query)
        
    if arge.battery:
        FileDir=AppInputDir+"\\module_log\\batterystat221106160538"
        batteryR=re.compile(r'\d{6} \d\d:\d\d:\d\d.\d{3}.*\"')
        parseR=re.compile(r'\"(.*?)\"')
        with open(FileDir, 'r') as f:
            k=f.read()
        col=['datetime', 'percent', 'status', 'devstatus', 'service', 'fgbg']
        df=pd.DataFrame(columns=col)
        batteryL=batteryR.findall(k)
        Bdate=[]
        Bpercent=[]
        Bstatus=[]
        Devicestatus=[]
        deviceApp=[]
        fgbg=[]
        for _n, i in enumerate(batteryL):
            splitedLog=i.split("(")
            Bdate.append(datetime.datetime.strptime(str(splitedLog[0])[:19], "%y%m%d %H:%M:%S.%f"))
            Bpercent.append(int(list(splitedLog[0].split(" "))[-1]))
            Bstatus.append(str(splitedLog[1])[0])
            Batinfo=parseR.findall(splitedLog[1])
            Devicestatus.append(Batinfo[0])
            if Devicestatus[-1] in ["wkup", "susp", "chg", "dchg"]:
                deviceApp.append(" ")
                fgbg.append(" ")
            else:
                deviceApp.append(str(Batinfo[1]))
                if Devicestatus=="app": fgbg.append(Batinfo[2])
                else: fgbg.append(" ")

        df=pd.DataFrame({'Bdate': Bdate, 'Bpercent': Bpercent, 'Bstatus': Bstatus, 'Devstatus': Devicestatus, 'Devapp': deviceApp, 'fgbg': fgbg})
        df.to_json(AppOutputDirMod+'\\7_battrystat.json', orient='records')
        df2=df[df['Bpercent']>=0]
        plt.figure(figsize=(len(Bdate)/250,(max(Bpercent)-min(Bpercent))*3/10))
        plt.subplot(3,1,1)
        plt.axis('auto')
        plt.title('Line Graph')
        plt.plot(Bdate, Bpercent)

        plt.subplot(3,1,2)
        plt.axis('auto')
        plt.title('Scatter Plot')
        plt.plot(df2['Bdate'], df2['Bpercent'], 'bo', markersize=3)


        plt.subplot(3,1,3)
        plt.axis('auto')
        plt.title('Plus(red) and Minus(blue)')
        dfplus=df2[df2['Bstatus']=="+"]
        dfminus=df2[df2['Bstatus']=="-"]
        plt.plot(dfplus['Bdate'], dfplus['Bpercent'], 'ro', markersize=3)
        plt.plot(dfminus['Bdate'], dfminus['Bpercent'], 'bo', markersize=3)
        plt.savefig(AppOutputDirMod+f'\\7_batterystat.jpg')
        
        dockercheck()
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\7_battrystat.json' + "-A 'batterystat'"
        subprocess.check_output(elastic_query)
        
    if arge.res:
        FileDir=AppInputDir+"\\module_log\\resourced_20221106160537.log"
        with open(FileDir, 'r') as f:
            k=f.read()
        lins=k.split("inde")
        colu=['index','type', 'pkgname', 'appid', 'lru', 'watchdog_exclude', 'runtime_exclude', 'flags', 'state', 'main_pid', 'oomscore', 'memory rss', 'utime', 'stime', 'starttime']
        df=pd.DataFrame(columns=colu)
        for i in lins[1:]:
            i=i.replace('\n\t', ',')
            t=i.split(',')
            temp=[]
            for k in t:
                temp.append((list(k.split(':'))[1])[1:].strip('\n'))
            df=pd.concat([df, pd.DataFrame([temp], columns=colu)], axis=0, ignore_index=True)
        df.to_json(AppOutputDirMod+'\\8_resourced.json', orient='records')

        dockercheck()
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\8_resourced.json' + "-A 'resources'"
        subprocess.check_output(elastic_query)
        
    if arge.appuse:
        FileDir=AppInputDir+"\\var_log\\appfw\\amd\\amd.log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        dic={}
        for line in k:    
            index=line[1:7]
            time=line[9:28]
            status=line[29:45]
            pkg=line[46:-1]
            dic[(index.strip(' '))]={'Time': time, 'Status': status, 'Package': pkg}
        with open(AppOutputVar+'\\9_amd.log.json', 'w') as fp:
            json.dump(dic, fp)

        dockercheck()
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\9_amd.log.json' + "-A 'appusedlog'"
        subprocess.check_output(elastic_query)
        
    if arge.appinst:
        r1=re.compile(r'\[(.+UTC)\]')
        r2=re.compile(r'\[(\d+)\]')
        r3=re.compile(r'pkgid:(.+)\|mode')
        r4=re.compile(r'mode:(.+)\|')
        r5=re.compile(r'\|([A-Z]+)$')
        a=[r1,r2,r3,r4,r5]
        FileDir=AppInputDir+"\\var_log\\appfw\\app-installers\\installation-history.log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        tw=[[ast.findall(i)[0] for ast in a] for i in k]
        lw=pd.DataFrame(tw, columns=['Time', 'Number', 'Pkgid', 'Mode', 'Status'])
        lw.to_json(AppOutputVar+'\\10_installation-history.json', orient='records')

        dockercheck()
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\10_installation-history.json' + "-A 'appinstalllog'"
        subprocess.check_output(elastic_query)
        
    if arge.bootcount:
        FileDir=AppInputDir+"\\var_log\\ghost\\boot\\bootcount"
        with open(FileDir, 'r') as f:
            k=f.read()
        print(k)
        with open(AppOutputVar+'\\11_boot', 'w') as fp:
            json.dump({'Boot': k}, fp)

    if arge.all:
        CSCV=re.compile(r'CSC Version : ([0-9A-Z]{12})')
        CSCC=re.compile(r'Sales code : ([A-Z]{3})')
        FileDir=AppInputDir+"\\module_log\\csc\\csc-default\\output\\csc-verification-report.log"
        with open(FileDir, 'r') as f:
            k=f.read()
        CSC_Version=str(CSCV.findall(k)[0])
        Region_code=str(CSCC.findall(k)[0])

        with open(AppOutputDirMod+'\\1_CSCversion.json', 'w') as fp:
            json.dump({'CSC_Version':CSC_Version, 'Region_code':Region_code}, fp)
        print({'CSC_Version':CSC_Version, 'Region_code':Region_code})
        
        SWC=re.compile(r'/([A-Z]{3})/')
        FileDir=AppInputDir+"\\module_log\\csc\\csc-default\\SW_Configuration.xml"
        with open(FileDir, 'r', encoding="utf-8") as f:
            k=f.read()
        SWCall=SWC.findall(k)
        print("Available Sales Number : ", len(SWCall))
        with open(AppOutputDirMod+'\\2_CSCCode.json', 'w') as fp:
            json.dump({'Available Sales Code':SWCall}, fp)
            
        vconfr=re.compile(r'value = (\d+)')
        FileDir=AppInputDir+"\\module_log\\gps\\vconf"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        dic={}
        for t in k:
            print(t[:-1])
            dic[t.split(',')[0]]=vconfr.findall(t.split(',')[1])[0]
        with open(AppOutputDirMod+'\\3_Vconf.json', 'w') as fp:
            json.dump(dic, fp)
            
        AppStartInfoR=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} START .*')
        AppStopInfoR=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} STOP .*')
        AppGPSInfoR=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} .* pos -> .* \[.*\] - \[.*\]')
        AppGPSInfoR2=re.compile(r'\d\d\/\d\d \d\d:\d\d:\d\d.\d{3} .* pos -> .* \[.*\] - \[([\dx]*) : ([\dx]*)\]')
        FileDir=AppInputDir+"\\module_log\\gps\\location.tar.gz"
        with tempfile.TemporaryDirectory() as tmpdir:
            file=tarfile.open(FileDir)
            file.extractall(tmpdir)
            file.close()
            print(os.listdir(tmpdir))
            for file in os.listdir(tmpdir):
                time=[]
                x=[]
                y=[]
                x_accum=[]
                y_accum=[]
                if "dump_gps" in file:
                    with open(tmpdir+"\\"+file, 'r') as f:
                        k=f.read()
                        AppStartInfo=AppStartInfoR.findall(k)
                        AppStopInfo=AppStopInfoR.findall(k)
                        AppGPSInfo=AppGPSInfoR.findall(k)
                    Appstartlist=[]
                    Appstartdict={}
                    for i in AppStartInfo:
                        #10/26 11:17:52.821 START COMPANION-WPS from [lbs-server/get_ref_location]
                        strs=i.split('START')
                        Appstartdict['Time']=strs[0]
                        Appstartdict['Info']=(strs[1]).split('from')[0]
                        Appstartdict['Service']=((strs[1]).split('from')[1])[1:]
                        Appstartlist.append(Appstartdict)
                    Appstoplist=[]
                    Appstopdict={}
                    for i in AppStopInfo:
                        strs=i.split('STOP')
                        Appstopdict['Time']=strs[0]
                        Appstopdict['Info']=(strs[1]).split('from')[0]
                        Appstopdict['Service']=((strs[1]).split('from')[1])[1:]
                        Appstoplist.append(Appstopdict)
                        print(Appstopdict)
                        print(i)
                    Sensorinfo=[]
                    num=[]
                    x_real=[]
                    y_real=[]
                    for i in AppGPSInfo:
                        time.append(datetime.strptime(i[:18], "%m/%d %H:%M:%S.%f"))
                        #[3x.4x6x0x : 1x7.x3x5x1]
                        #x.append(i[-23:-15])
                        #y.append(i[-20:-3])
                        #11/06 10:36:28.416 companion-wps pos -> FW : [0] - [3x.4x6x0x : 1x7.x3x5x4]
                        x.append(int(i[-16]))
                        y.append(int(i[-4]))
                        x_real.append(i[-23:-14])
                        y_real.append(i[-11:-1])
                        Sensorinfo.append(i.split(' ')[2])
                        num.append(i.split(' ')[7][1:-1])
                    x_accum.append(x[0])
                    y_accum.append(y[0])
                    for i in range(len(x)-1):
                        x_accum.append(x_accum[i])
                        if (x[i+1]-(x_accum[i]%10)+10)%10<=5:
                            while x_accum[i+1]%10!=x[i+1]:
                                x_accum[i+1]=x_accum[i+1]+1
                        else:
                            while x_accum[i+1]%10!=x[i+1]:
                                x_accum[i+1]=x_accum[i+1]-1
                        y_accum.append(y_accum[i])
                        if (y[i+1]-(y_accum[i]%10)+10)%10<=5:
                            while y_accum[i+1]%10!=y[i+1]:
                                y_accum[i+1]=y_accum[i+1]+1
                        else:
                            while y_accum[i+1]%10!=y[i+1]:
                                y_accum[i+1]=y_accum[i+1]-1
                    for i in range(len(y_accum)):
                        y_accum[i]=y_accum[i]*10
                        #print(x[i]/10, y[i], x_accum[i]/10, y_accum[i])
                    
                    df=pd.DataFrame({'Date':[datetime.strftime(x, "%m.%d %H:%M:%S.%f") for x in time],'Sensorinfo':Sensorinfo, 'num':num, 'X':x_real, 'Y':y_real, 'X_accum':x_accum, 'Y_accum':y_accum})
                    plt.figure(figsize=((max(y_accum)-min(y_accum))/200,(max(x_accum)-min(x_accum))/200))
                    #plt.plot(y_accum, x_accum,color='skyblue',marker='o', markerfacecolor='blue',markersize=6)
                    #1틱: 대략 11.1미터, 곧 초속 50미터 이하의 범위에서는 (시속 200km 이하) 유효할 것으로 예상
                    plt.axis('off')
                    plt.title(file)
                    plt.plot(y_accum, x_accum,'bo', markersize=3)
                    plt.savefig(AppOutputDirMod+f'\\4_2_locationIMG_{file}.jpg')
                    
                    dic={'START':Appstartlist, 'STOP':Appstoplist}
                    with open(AppOutputDirMod+f'\\4_1_locationSTARTSTOP_{file}.json', 'w') as fp:
                        json.dump(dic, fp)
                    df.to_json(AppOutputDirMod+f'\\4_2_locationDUMP_{file}.json', orient='records')
                else:
                    pass        
    
        
        FileDir=AppInputDir+"\\module_log\\power\\pm_reset_log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        di={}
        di['LOGTIME']=k[0][:-1]
        lis={}
        for i in k[2:]:
            if i=='\n': break
            lis[i[:24]]=i.split(' ')[-1][:-1]
        di['LOG']=lis
        with open(AppOutputDirMod+'\\5_pm_reset_log.json', 'w') as fp:
            json.dump(di, fp)
            
        systemtimeR=re.compile(r'system time : (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \(.*\)')
        timezoneR=re.compile(r'timezone\s+: .* \(.*\)')
        FileDir=AppInputDir+"\\module_log\\power\\pm_time_history"
        with open(FileDir, 'r') as f:
            k=f.read()
        txt=k.split('\n\n')
        timehistoryheader={}
        for l in txt[2].split('\n'):
            timehistoryheader[l.split(':')[0].strip(' ')]=(':'.join( l.split(':')[1:])).strip(' ')
            
        timelogheader=re.split(r'\s\s+', txt[3].split('\n')[0])[1:]
        df=pd.DataFrame(columns=timelogheader)
        dividepoint=[21,28,44,50,65,83,107,129,141]
        for line in txt[3].split('\n')[1:]:
            dat=[]
            st=0
            for p in dividepoint:
                dat.append(line[st:p-1].strip()) 
                st=p-1
            dat.append(line[st:].strip())
            df=pd.concat([df, pd.DataFrame([dat], columns=timelogheader)], ignore_index=True)
        di={'Info':timehistoryheader}
        with open(AppOutputDirMod+'\\6_1_pm_time_history_LOGINFO.json', 'w') as fp:
            json.dump(di, fp)
        df.to_json(AppOutputDirMod+'\\6_2_pm_time_history_LOG.json', orient='records')
        
        FileDir=AppInputDir+"\\module_log\\batterystat221106160538"
        batteryR=re.compile(r'\d{6} \d\d:\d\d:\d\d.\d{3}.*\"')
        parseR=re.compile(r'\"(.*?)\"')
        with open(FileDir, 'r') as f:
            k=f.read()
        col=['datetime', 'percent', 'status', 'devstatus', 'service', 'fgbg']
        df=pd.DataFrame(columns=col)
        batteryL=batteryR.findall(k)
        Bdate=[]
        Bpercent=[]
        Bstatus=[]
        Devicestatus=[]
        deviceApp=[]
        fgbg=[]
        for _n, i in enumerate(batteryL):
            splitedLog=i.split("(")
            Bdate.append(datetime.strptime(str(splitedLog[0])[:19], "%y%m%d %H:%M:%S.%f"))
            Bpercent.append(int(list(splitedLog[0].split(" "))[-1]))
            Bstatus.append(str(splitedLog[1])[0])
            Batinfo=parseR.findall(splitedLog[1])
            Devicestatus.append(Batinfo[0])
            if Devicestatus[-1] in ["wkup", "susp", "chg", "dchg"]:
                deviceApp.append(" ")
                fgbg.append(" ")
            else:
                deviceApp.append(str(Batinfo[1]))
                if Devicestatus=="app": fgbg.append(Batinfo[2])
                else: fgbg.append(" ")

        df=pd.DataFrame({'Bdate': Bdate, 'Bpercent': Bpercent, 'Bstatus': Bstatus, 'Devstatus': Devicestatus, 'Devapp': deviceApp, 'fgbg': fgbg})
        df.to_json(AppOutputDirMod+'\\7_battrystat.json', orient='records')
        df2=df[df['Bpercent']>=0]
        plt.figure(figsize=(len(Bdate)/250,(max(Bpercent)-min(Bpercent))*3/10))
        plt.subplot(3,1,1)
        plt.axis('auto')
        plt.title('Line Graph')
        plt.plot(Bdate, Bpercent)

        plt.subplot(3,1,2)
        plt.axis('auto')
        plt.title('Scatter Plot')
        plt.plot(df2['Bdate'], df2['Bpercent'], 'bo', markersize=3)


        plt.subplot(3,1,3)
        plt.axis('auto')
        plt.title('Plus(red) and Minus(blue)')
        dfplus=df2[df2['Bstatus']=="+"]
        dfminus=df2[df2['Bstatus']=="-"]
        plt.plot(dfplus['Bdate'], dfplus['Bpercent'], 'ro', markersize=3)
        plt.plot(dfminus['Bdate'], dfminus['Bpercent'], 'bo', markersize=3)
        plt.savefig(AppOutputDirMod+f'\\7_batterystat.jpg')    
        
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\7_battrystat.json' + "-A 'batterystat'"
        subprocess.check_output(elastic_query)
            
        FileDir=AppInputDir+"\\module_log\\resourced_20221106160537.log"
        with open(FileDir, 'r') as f:
            k=f.read()
        lins=k.split("inde")
        colu=['index','type', 'pkgname', 'appid', 'lru', 'watchdog_exclude', 'runtime_exclude', 'flags', 'state', 'main_pid', 'oomscore', 'memory rss', 'utime', 'stime', 'starttime']
        df=pd.DataFrame(columns=colu)
        for i in lins[1:]:
            i=i.replace('\n\t', ',')
            t=i.split(',')
            temp=[]
            for k in t:
                temp.append((list(k.split(':'))[1])[1:].strip('\n'))
            df=pd.concat([df, pd.DataFrame([temp], columns=colu)], axis=0, ignore_index=True)
        df.to_json(AppOutputDirMod+'\\8_resourced.json', orient='records')
        
        FileDir=AppInputDir+"\\var_log\\appfw\\amd\\amd.log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        dic={}
        for line in k:    
            index=line[1:7]
            time=line[9:28]
            status=line[29:45]
            pkg=line[46:-1]
            dic[(index.strip(' '))]={'Time': time, 'Status': status, 'Package': pkg}
        with open(AppOutputVar+'\\9_amd.log.json', 'w') as fp:
            json.dump(dic, fp)
        
        r1=re.compile(r'\[(.+UTC)\]')
        r2=re.compile(r'\[(\d+)\]')
        r3=re.compile(r'pkgid:(.+)\|mode')
        r4=re.compile(r'mode:(.+)\|')
        r5=re.compile(r'\|([A-Z]+)$')
        a=[r1,r2,r3,r4,r5]
        FileDir=AppInputDir+"\\var_log\\appfw\\app-installers\\installation-history.log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        tw=[[ast.findall(i)[0] for ast in a] for i in k]
        lw=pd.DataFrame(tw, columns=['Time', 'Number', 'Pkgid', 'Mode', 'Status'])
        lw.to_json(AppOutputVar+'\\10_installation-history.json', orient='records')    
            
        FileDir=AppInputDir+"\\var_log\\ghost\\boot\\bootcount"
        with open(FileDir, 'r') as f:
            k=f.read()
        print(k)
        with open(AppOutputVar+'\\11_boot', 'w') as fp:
            json.dump({'Boot': k}, fp)    
        
        dockercheck()
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + f'\\4_2_locationDUMP_{file}.json' + "-A 'gpslog'"
        subprocess.check_output(elastic_query)
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\5_pm_reset_log.json' + "-A 'rebootlog'"
        subprocess.check_output(elastic_query)
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\6_2_pm_time_history_LOG.json' + "-A 'timeinfo'"
        subprocess.check_output(elastic_query)
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\7_battrystat.json' + "-A 'batterystat'"
        subprocess.check_output(elastic_query)
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputDirMod + '\\8_resourced.json' + "-A 'resources'"
        subprocess.check_output(elastic_query)
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputVar + '\\9_amd.log.json' + "-A 'appusedlog'"
        subprocess.check_output(elastic_query)
        elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + AppOutputVar + '\\10_installation-history.json' + "-A 'appinstalllog'"
        subprocess.check_output(elastic_query)