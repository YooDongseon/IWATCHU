import argparse
import os
import json
import subprocess
import pandas as pd
import sys
import xml.etree.ElementTree as ET
import sqlite3

def main(path):                                                                                                                                # Tizen OS debug level 메인
    
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
 
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # connect to the SQlite databases
    def openConnection(pathToSqliteDb):
        connection = sqlite3.connect(pathToSqliteDb)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return connection, cursor


    def getAllRecordsInTable(table_name, pathToSqliteDb):
        conn, curs = openConnection(pathToSqliteDb)
        conn.row_factory = dict_factory
        curs.execute("SELECT * FROM '{}' ".format(table_name))
        # fetchall as result
        results = curs.fetchall()
        # close connection
        conn.close()
        return json.dumps(results)


    def sqliteToJson(pathToSqliteDb, dirobj):
        connection, cursor = openConnection(pathToSqliteDb)
        # select all the tables from the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # for each of the tables , select all the records from the table
        for table_name in tables:
            # Get the records in table
            results = getAllRecordsInTable(table_name['name'], pathToSqliteDb)

            # generate and save JSON files with the table name for each of the database tables and save in results folder
            with open(dirobj+'\\'+table_name['name']+'.json', 'w') as the_file:
                the_file.write(results)
        # close connection
        connection.close()
    
    Select = argparse.ArgumentParser(description='Smart Watch analyzer for Tizen OS in debug level')
    
    result_path_defalut = "{}".format(os.getcwd())
    
    Select.add_argument("Tizen", metavar='N', action='store')
    Select.add_argument("app", metavar='N', action='store')
    Select.add_argument('path', metavar='N', type = str, action='store') 
    Select.add_argument("--stat", dest="stat", action='store_true', help="At Tizen os in debug level, get devide information")  
    Select.add_argument("--hstat", dest="hstat", action='store_true', help="At Tizen os in debug level, get host device information")
    Select.add_argument("--instapp", dest="instapp", action='store_true', help="At Tizen os in debug level, get a list of installed app ") 
    Select.add_argument("--acc", dest="account", action='store_true', help="At Tizen os in debug level, get account information. And upload json outputs to elk-stack")
    Select.add_argument("--comp", dest="companion", action='store_true', help="At Tizen os in debug level, get a connected device inform. And upload json outputs to elk-stack")
    Select.add_argument("--battery", dest="battery", action='store_true', help="At Tizen os in debug level, get information of battery usage and show graph as jpg. And upload json outputs to elk-stack")
    Select.add_argument("--wnoti", dest="wnoti", action='store_true', help="At Tizen os in debug level, get information of wnoti-service.db. And upload json outputs to elk-stack")
    Select.add_argument("--ssacc", dest="ssacc", action='store_true', help="At Tizen os in debug level, get log of samsung account. And upload json outputs to elk-stack")
    Select.add_argument("--contact", dest="contact", action='store_true', help="At Tizen os in debug level, get db of contacts. And upload json outputs to elk-stack")
    Select.add_argument("--msg", dest="msg", action='store_true', help="At Tizen os in debug level, get db of msg. And upload json outputs to elk-stack")
    Select.add_argument("--weather", dest="weather", action='store_true', help="At Tizen os in debug level, get db of weather. And upload json outputs to elk-stack")
    Select.add_argument("--sensor", dest="sensor", action='store_true', help="At Tizen os in debug level, get data of sensor. And upload json outputs to elk-stack")
    Select.add_argument("--batmon", dest="batmon", action='store_true', help="At Tizen os in debug level, get data of battery monitor. And upload json outputs to elk-stack")
    Select.add_argument("--reset", dest="reset", action='store_true', help="At Tizen os in debug level, get data of reboot")
    Select.add_argument("--calendar", dest="calendar", action='store_true', help="At Tizen os in debug level, get data of calendar. And upload json outputs to elk-stack")
    Select.add_argument("--notice", dest="notice", action='store_true', help="At Tizen os in debug level, get data of notification sensor. And upload json outputs to elk-stack")
    Select.add_argument("--alarm", dest="alarm", action='store_true', help="At Tizen os in debug level, get data of alarm. And upload json outputs to elk-stack")
    Select.add_argument("--reminder", dest="reminder", action='store_true', help="At Tizen os in debug level, get data of reminder alarm. And upload json outputs to elk-stack")
    Select.add_argument("--history", dest="history", action='store_true', help="At Tizen os in debug level, get data of application history. And upload json outputs to elk-stack")
    Select.add_argument("--all", dest="all", action='store_true', help="At Tizen os in application level, get a all information of above. And upload json outputs to elk-stack")
    arge = Select.parse_args()
    
    DebInputDir = path
    DebOutputDir=result_path_defalut + "\\TizenOS\\Debug level"
    os.makedirs(DebOutputDir, exist_ok=True)
    
    if arge.stat:
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.w-manager-service\\data\\WearableStatus.xml"
        with open(FileDir, 'r', encoding='utf-8') as f:
            etree=ET.parse(f)
        root=etree.getroot()
        dict={}
        for child in root[0]:
            if child.text== "\n   ":
                for k in child:
                    pass
            elif child.text not in ["", "None", None, "\n   "]:
                dict[child.tag]=child.text
            else: pass
        print(dict)
        with open(DebOutputDir+'\\11_WearableStatus.xml.json', 'w') as fp:
            json.dump(dict, fp)
    
    if arge.hstat:
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.w-manager-service\\data\\Hoststatus.xml"
        with open(FileDir, 'r', encoding='utf-8') as f:
            etree=ET.parse(f)
        root=etree.getroot()
        dict={}
        for child in root[0]:
            if child.text== "\n   ":
                for k in child:
                    pass
            elif child.text not in ["", "None", None, "\n   "]:
                dict[child.tag]=child.text
            else: pass
        print(dict)
        with open(DebOutputDir+'\\12_Hoststatus.xml.json', 'w') as fp:
            json.dump(dict, fp)
            
    if arge.instapp:
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.w-manager-service\\data\\wapplist.xml"
        with open(FileDir, 'r', encoding='utf-8') as f:
            etree=ET.parse(f)
        root=etree.getroot()
        dict={}
        for child in root[0]:
            if child.text== "\n   ":
                for k in child:
                    pass
            elif child.text not in ["", "None", None, "\n   "]:
                dict[child.tag]=child.text
            else: pass
        print(dict)
        with open(DebOutputDir+'\\13_wappstatus.json', 'w') as fp:
            json.dump(dict, fp)
    
    if arge.account:
        FileDir=DebInputDir+"\\opt\\dbspace\\5001\\.account.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        df
        pathToSqliteDb = FileDir
        folder='\\14_account.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(pathToSqliteDb, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.companion: 
        FileDir=DebInputDir+"\\opt\\usr\\dbspace\\.CompanionInfo.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        pathToSqliteDb = FileDir
        folder='\\15_CompanionInfo.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(pathToSqliteDb, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.battery:
        FileDir=DebInputDir+"\\opt\\usr\\dbspace\\.resourced-heart-default.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\16_resourced-heart-default'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.wnoti:
        FileDir=DebInputDir+"\\opt\\usr\\dbspace\\.wnoti-service.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\17_wnoti-service'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.ssacc:
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.tizen.samsung-account\\data\\samsungaccount.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[4][0]};', con=con)
        folder='\\18_samsungaccount'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)  
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.contact:
        FileDir=DebInputDir+"\\home\\owner\\.applications\\dbspace\\privacy\\.contacts-svc.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\19_contacts-svc'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.msg:
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.message\\data\\dbspace\\.msg-consumer-server.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[3][0]};', con=con)
        folder='\\20_msg-consumer-server'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.weather:
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\apps_rw\\.shared\\com.samsung.weather\\data\\db\\.weather.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\21_weather.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.sensor:
        FileDir=DebInputDir+"\\opt\\dbspace\\.context-sensor-recorder.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[3][0]};', con=con)
        folder='\\22_context-sensor-recorder.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.batmon:
        FileDir=DebInputDir+"\\opt\\dbspace\\.battery-monitor.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[3][0]};', con=con)
        folder='\\23_battery-monitor.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.reset:
        FileDir=DebInputDir+"\\opt\\usr\\data\\power\\siop_reset_log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        listt=[]
        for _n, line in enumerate(k):
            listt.append({'Index': _n+1, 'Date': ' '.join([a for a in line.split(' ')[:-1]]), 'Status': line.split(' ')[-1][:-1]})
        with open(DebOutputDir+'\\26_pm_reset_log', 'w') as fp:
            json.dump(listt, fp)
        
    if arge.calendar:
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\apps_rw\\com.samsung.w-calendar2\\data\\.calendar_consumer.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\25_calendar_consumer.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.notice:
        FileDir=DebInputDir+"\\opt\\dbspace\\.notification.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\27_notification.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.alarm:
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\apps_rw\\com.samsung.alarm-solis\\data\\.alarm.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\28_alarm.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.reminder:
        FileDir=DebInputDir+"\\opt\\usr\\apps\\com.samsung.w-reminder\\data\\.reminder.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\29_reminder.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.history:
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\.applications\\dbspace\\.context-app-history.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\30_context-app-history.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        dockercheck()
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
            
    if arge.all:
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.w-manager-service\\data\\WearableStatus.xml"
        with open(FileDir, 'r', encoding='utf-8') as f:
            etree=ET.parse(f)
        root=etree.getroot()
        dict={}
        for child in root[0]:
            if child.text== "\n   ":
                for k in child:
                    pass
            elif child.text not in ["", "None", None, "\n   "]:
                dict[child.tag]=child.text
            else: pass
        print(dict)
        with open(DebOutputDir+'\\11_WearableStatus.xml.json', 'w') as fp:
            json.dump(dict, fp)
            
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.w-manager-service\\data\\Hoststatus.xml"
        with open(FileDir, 'r', encoding='utf-8') as f:
            etree=ET.parse(f)
        root=etree.getroot()
        dict={}
        for child in root[0]:
            if child.text== "\n   ":
                for k in child:
                    pass
            elif child.text not in ["", "None", None, "\n   "]:
                dict[child.tag]=child.text
            else: pass
        print(dict)
        with open(DebOutputDir+'\\12_Hoststatus.xml.json', 'w') as fp:
            json.dump(dict, fp)
            
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.w-manager-service\\data\\wapplist.xml"
        with open(FileDir, 'r', encoding='utf-8') as f:
            etree=ET.parse(f)
        root=etree.getroot()
        dict={}
        for child in root[0]:
            if child.text== "\n   ":
                for k in child:
                    pass
            elif child.text not in ["", "None", None, "\n   "]:
                dict[child.tag]=child.text
            else: pass
        print(dict)
        with open(DebOutputDir+'\\13_wappstatus.json', 'w') as fp:
            json.dump(dict, fp)
            
        FileDir=DebInputDir+"\\opt\\dbspace\\5001\\.account.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        df
        pathToSqliteDb = FileDir
        folder='\\14_account.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(pathToSqliteDb, DebOutputDir+folder)
            
        
        FileDir=DebInputDir+"\\opt\\usr\\dbspace\\.CompanionInfo.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        pathToSqliteDb = FileDir
        folder='\\15_CompanionInfo.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(pathToSqliteDb, DebOutputDir+folder)
            
        
        FileDir=DebInputDir+"\\opt\\usr\\dbspace\\.resourced-heart-default.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\16_resourced-heart-default'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
    
        
        FileDir=DebInputDir+"\\opt\\usr\\dbspace\\.wnoti-service.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\17_wnoti-service'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.tizen.samsung-account\\data\\samsungaccount.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master;')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[4][0]};', con=con)
        folder='\\18_samsungaccount'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\home\\owner\\.applications\\dbspace\\privacy\\.contacts-svc.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\19_contacts-svc'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
        FileDir=DebInputDir+"\\home\\owner\\apps_rw\\com.samsung.message\\data\\dbspace\\.msg-consumer-server.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[3][0]};', con=con)
        folder='\\20_msg-consumer-server'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\apps_rw\\.shared\\com.samsung.weather\\data\\db\\.weather.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[2][0]};', con=con)
        folder='\\21_weather.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\opt\\dbspace\\.context-sensor-recorder.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[3][0]};', con=con)
        folder='\\22_context-sensor-recorder.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\opt\\dbspace\\.battery-monitor.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[3][0]};', con=con)
        folder='\\23_battery-monitor.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
        
        FileDir=DebInputDir+"\\opt\\usr\\data\\power\\siop_reset_log"
        with open(FileDir, 'r') as f:
            k=f.readlines()
        listt=[]
        for _n, line in enumerate(k):
            listt.append({'Index': _n+1, 'Date': ' '.join([a for a in line.split(' ')[:-1]]), 'Status': line.split(' ')[-1][:-1]})
        with open(DebOutputDir+'\\26_pm_reset_log', 'w') as fp:
            json.dump(listt, fp)
            
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\apps_rw\\com.samsung.w-calendar2\\data\\.calendar_consumer.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\25_calendar_consumer.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\opt\\dbspace\\.notification.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\27_notification.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\apps_rw\\com.samsung.alarm-solis\\data\\.alarm.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\28_alarm.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
            
        FileDir=DebInputDir+"\\opt\\usr\\apps\\com.samsung.w-reminder\\data\\.reminder.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\29_reminder.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        
            
        '''    
        FileDir=DebInputDir+"\\opt\\usr\\home\\owner\\.applications\\dbspace\\.context-app-history.db"
        con=sqlite3.connect(FileDir)
        cur=con.cursor()
        cur.execute('select name from sqlite_master where type="table";')
        tablename=cur.fetchall()
        print(tablename)
        df=pd.read_sql(f'select * from {tablename[0][0]};', con=con)
        folder='\\30_context-app-history.db'
        os.makedirs(DebOutputDir+folder, exist_ok=True)
        sqliteToJson(FileDir, DebOutputDir+folder)
        '''
        #도커 업로드 부분
        dockercheck()
        folder='\\14_account.db'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)
        
        
        folder='\\15_CompanionInfo.db'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\16_resourced-heart-default'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\17_wnoti-service'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\18_samsungaccount'
        file_list = os.listdir(DebOutputDir+folder)  
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\19_contacts-svc'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\20_msg-consumer-server'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\21_weather.db'
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\22_context-sensor-recorder.db'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\23_battery-monitor.db'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\25_calendar_consumer.db'
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\27_notification.db'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\28_alarm.db'
        file_list = os.listdir(DebOutputDir+folder)
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\29_reminder.db'
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)

        folder='\\30_context-app-history.db'
        file_list = os.listdir(DebOutputDir+folder)    
        for i in file_list: 
            log_name = i[:-5]
            elastic_query = "curl -XPUT http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '@" + DebOutputDir + folder + i + "-A '" + log_name +"'"
            subprocess.check_output(elastic_query)