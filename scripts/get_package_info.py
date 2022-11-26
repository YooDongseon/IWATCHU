from ppadb.client import Client as AdbClient

client = AdbClient(host='127.0.0.1', port=5037)
devices = client.devices()
device1 = devices[0]
installed_packages=[]



'''    
def dump_command(connect):
    file_obj = connect.socket.makefile()
    
    f = open("C:/users/jsj97/desktop/package_list.txt", 'w')
    while True:
        data = "{}".format(file_obj.readline().strip().replace("package:",""))
        next_line="\n"
        if file_obj.readline().strip() == "" :
            break
        f.write(data)
        f.write(next_line)
        installed_packages.append(data)

    file_obj.close()
    connect.close()
    f.close()
'''

def read_result(connection):
    while True:
        
        data = connection.read(100000000)
        if not data:
            break
        f.write(data.decode('utf-8'))
        print(data.decode('utf-8'))
    
    f.close()
    connection.close()

device1.shell("pm list packages -3 > data/local/tmp/package_list.txt")
device1.pull("data/local/tmp/package_list.txt", "c:\\users\\jsj97\\desktop\\script_result\\package_list.txt")
device1.shell("rm data/local/tmp/package_list.txt")
#print(installed_packages)

with open("c:\\users\\jsj97\\desktop\\script_result\\package_list.txt") as f:
    lines = f.readlines()

for i in range(len(lines)):
    installed_packages.append(lines[i].replace("package:","").replace("\n",""))


for i in range(len(installed_packages)):
    print(installed_packages[i])
    f = open("C:/users/jsj97/desktop/script_result/package_info.txt", 'a')
    f.write("\n"+installed_packages[i]+"\n")
    device1.shell("dumpsys package " + installed_packages[i] + " | grep -e 'firstInstallTime' -e 'permission'", handler=read_result)
    