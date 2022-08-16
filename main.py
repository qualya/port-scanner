from mcstatus import JavaServer #https://github.com/py-mine/mcstatus
import os
currentDir = os.getcwd()
from tqdm import tqdm
from time import sleep, time
import requests
import bs4
import socket
import ipaddress
import threading
socket.setdefaulttimeout(0.5)

startingThreads = threading.active_count()+1

paths = [(currentDir + "/servers"), (currentDir + "/servers-data")]
for path in paths:
    if os.path.isdir(path) == False:
        os.mkdir(path)



def check_port(ip, port, outputMode):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        result = sock.connect_ex((ip,port))
        
        if outputMode == "response":
            return result
        
        if outputMode == "file":
            if result == 0:
                serversList.append(str(ip) + ":" + str(port))
                    
        sock.close()
        
    except Exception as e:
        print(e)
        if outputMode == "response":
            return "Error"



def getWebpage(address, outputMode, showPort):
    if showPort == False:
        ip, port = address.split(":")
    if showPort == True:
        ip = address
        
    url = "http://" + address
    try:
        response = requests.get(url, verify=False, timeout=15)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        title = soup.title.text.replace("|", "!")
        title.replace("\n", " ")
        if title == "":
            title = "None"
        htmlData = [ip, str(response.status_code), title]
    
    except Exception as error:
        if str(error) == "'NoneType' object has no attribute 'text'":
            htmlData = [ip, "None", "None"]
        else:
            htmlData = [ip, "Error", str(error)]
    
    if outputMode == "return":
        return htmlData
    if outputMode == "file":
        serverData.append("|".join(htmlData))



def getMC(address, outputMode, showPort):
    if showPort == False:
        ip, port = address.split(":")
    if showPort == True:
        ip = address
        
    try:
        server = JavaServer.lookup(address)
        status = server.status()
        #'description', 'favicon', 'latency', 'players', 'raw', 'version'
        
        base64img = status.favicon #favicon 1/1

        description = str(status.description).replace("|", "!").replace(":", ";").replace("\n", ":") #description 1/1
        
        versionName = str(status.version.name).replace("|", "!").replace("\n", " ") #version 1/2
        versionProtocol = str(status.version.protocol).replace("|", "!").replace("\n", " ") #version 2/2
        
        latencyPing = str(round(status.latency, 3)).replace("|", "!").replace("\n", " ") #latency 1/1
        
        onlinePlayers = str(status.players.online).replace("|", "!").replace("\n", " ") #players 1/4
        maxPlayers = str(status.players.max).replace("|", "!").replace("\n", " ") #players 2/4
        
        playerInfo = list()
        try:
            for player in status.players.sample:
                uuid = str(player.id).replace("|", "!").replace(":", ";").replace(",", ".") #players 3/4
                username = str(player.name).replace("|", "!").replace(":", ";").replace(",", ".") #players 4/4
                playerInfo.append(uuid + ":" + username)
        except:
            pass
        playerInfo = ",".join(playerInfo)
        if playerInfo == "":
            playerInfo = "None"
        playerInfo = playerInfo.replace("\n", " ")
        
        mcData = [ip, description, versionName, versionProtocol, latencyPing, onlinePlayers, maxPlayers, playerInfo]
        
        
    except Exception as error:
        mcData = [ip, "None"]
    
    
    if outputMode == "return":
        return mcData
    if outputMode == "file":
        serverData.append("|".join(mcData))



print("Do you want to find open servers/port scan [1], process server addresses [2], or extract server data from this program's file structure [3]?")
mode = input()
while mode not in ["1", "2", "3"]:
    print("\nInput must be '1', '2', or '3'.")
    mode = input()





if mode == "1":
    max_threads = 4096
    
    properInput = False
    while properInput == False:
        startingIP = input("\nStarting IP: ")
        endingIP = input("Ending IP: ")
        startingPort = input("Starting Port: ")
        endingPort = input("Ending Port: ")
        print()
        
        try:
            startingIP = int(ipaddress.IPv4Address(startingIP))
            endingIP = int(ipaddress.IPv4Address(endingIP))
            startingPort = int(startingPort)
            endingPort = int(endingPort)
            
            if startingPort in range(65536) and endingPort in range(65536):
                properInput = True
            else:
                print("Ports must be between 0 and 65535")
        
        except:
            print("You must input valid IP addresses and port numbers.")
    
    
    serversList = list()
    start = time()
    for ip_int in tqdm(range(startingIP, endingIP+1)):
        ip = str(ipaddress.IPv4Address(ip_int))
        for port in range(startingPort, endingPort+1):
            threading.Thread(target=check_port, args=[str(ip), port, "file"]).start()
            while threading.active_count() > max_threads: # limit the number of threads.
                sleep(1)
    while threading.active_count() > startingThreads:
        sleep(1)

    
    newIPs = 0
    for server in serversList:
        ip, port = server.split(":")
        path = currentDir + "/servers/" + ip.split(".")[0]
        filePath = path + "/" + str(port) + ".txt"
        if os.path.isdir(path) == False:
            os.mkdir(path)
            
        exists = False
        if os.path.exists(filePath):
            with open(filePath, "r") as serversFile:
                for line in serversFile:
                    if line.replace("\n", "") == ip:
                        exists = True
                serversFile.close()
        
        if exists == False:
            newIPs += 1
            with open(filePath, "a") as serversFile:
                serversFile.write(ip + "\n")
                serversFile.close()


    IPsSearched = endingIP-startingIP
    print("\n\nFound " + str(len(serversList)) + " open servers of " + str(IPsSearched) + " IPs searched.")
    print("Of " + str(len(serversList)) + " open servers, " + str(newIPs) + " were new.")
    elapsed = time()-start
    print("Elapsed time: " + str(elapsed) + " seconds")





if mode == "2":
    max_threads = 64
    
    print("\n\nDo you want to process the IPs as websites [1], or Minecraft servers [2]?")
    serverType = input()
    while serverType not in ["1", "2"]:
        print("\nInput must be '1', or '2'.")
        serverType = input()
    
    print("\n\nDo you want to type addresses individually [1], process a file [2], or process addresses using this program's file structure [3]?")
    processMode = input()
    while processMode not in ["1", "2", "3"]:
        print("\nInput must be '1', '2', or '3'.")
        processMode = input()


    if processMode == "1": #individual IP addresses
        running = True
        while running:
            ip = input("\n\nIP Address: ")
            if serverType == "1":
                print(getWebpage(ip, "return", True))
            if serverType == "2":
                print(getMC(ip, "return", True))


    if processMode == "2": #process a specified file
        filename = input("\n\nFilename: ")
        while os.path.exists(filename) == False:
            print("\nFile not found.")
            filename = input("Filename: ")
        
        addressList = list()
        with open(filename, "r") as ipFile:
            for line in ipFile:
                addressList.append(line.strip("\n"))
        
        
        print("\n\nWhat do you want the name of the output file to be?")
        outputFilename = input("Filename: ")
        
        
        serverData = list()
        for address in tqdm(addressList):
            if serverType == "1": #if the servers are websites
                threading.Thread(target=getWebpage, args=[address, "file", True]).start()
            if serverType == "2": #if the servers are Minecraft servers
                threading.Thread(target=getMC, args=[address, "file", True]).start()
            while threading.active_count() > max_threads: # limit the number of threads.
                sleep(1)
        while threading.active_count() > startingThreads:
            sleep(1)
        
        
        with open(outputFilename, "w", encoding="utf8") as serverDataFile:
            for line in serverData:
                serverDataFile.write(line + "\n")
            serverDataFile.close()


    if processMode == "3": #process IP addresses that have been found using the scanning feature
        print("\n\nWhat is the starting number (0-255) of the IP addresses?") #gets the starting number of the IP from the user (the folder name)
        properInput = False
        while not properInput:
            ipStart = input()
            if ipStart.isdigit():
                if 255 >= int(ipStart) >= 0:
                    if os.path.isdir(currentDir + "/servers/" + ipStart):
                        properInput = True
                    else:
                        print("\nThere are no scanned IPs starting with this number.")
                else:
                    print("\nThis is not a number from 0-255.")
            else:
                print("\nThis is not a valid number.")
        
        print("\n\nWhat is the port number (0-65535) of the IP addresses?") #gets the port number of the server from the user (the txt file name)
        properInput = False
        while not properInput:
            port = input()
            if port.isdigit():
                if 65535 >= int(port) >= 0:
                    if os.path.isfile(currentDir + "/servers/" + ipStart + "/" + port + ".txt"):
                        properInput = True
                    else:
                        print("\nThere are no scanned IPs with this port number.")
                else:
                    print("\nThis is not a number from 0-65535.")
            else:
                print("\nThis is not a valid number.")
        
        ipList = list() #stores all the ip addresses from the file
        with open((currentDir + "/servers/" + ipStart + "/" + port + ".txt"), "r") as serversFile:
            for line in serversFile:
                ipList.append(line.strip("\n"))
        
        if os.path.exists(currentDir + "/servers-data/" + ipStart) == False: #creates the same folder within the servers-data folder to store processed data
            os.mkdir(currentDir + "/servers-data/" + ipStart)
        
        serverData = list() #processes all of the IP addresses
        for ip in tqdm(ipList):
            address = ip + ":" + port
            if serverType == "1": #if the servers are websites
                threading.Thread(target=getWebpage, args=[address, "file", False]).start()
            if serverType == "2": #if the servers are Minecraft servers
                threading.Thread(target=getMC, args=[address, "file", False]).start()
            while threading.active_count() > max_threads: # limit the number of threads.
                sleep(1)
        while threading.active_count() > startingThreads:
            sleep(1)
        
        with open((currentDir + "/servers-data/" + ipStart + "/" + port + ".txt"), "w", encoding="utf8") as serverDataFile: #saves all of the data
            for line in serverData:
                serverDataFile.write(line + "\n")
            serverDataFile.close()





if mode == "3":
    print("\n\nDo you want to extract just addresses [1], or processed data too [2]?")
    extractType = input()
    while extractType not in ["1", "2"]:
        print("\nInput must be '1', or '2'.")
        extractType = input()
    if extractType == "1":
        path = currentDir + "/servers/"
    if extractType == "2":
        path = currentDir + "/servers-data/"
    folders = os.listdir(path)
    
    print("\n\nDo you want to extract data from all addresses [1], or all of specific ports [2]?")
    extractMode = input()
    while extractMode not in ["1", "2"]:
        print("\nInput must be '1', or '2'.")
        extractMode = input()
    
    
    includedPorts = []
    if extractMode == "2":
        print("\n\nInput the ports you want to extract, seperated by a comma, below.")
        includedPorts = input().split(",")
    
    
    print("\n\nWhat do you want the name of the output file to be?")
    outputFilename = input("Filename: ")
    
    
    serverData = []
    for folder in folders:
        files = os.listdir(path + folder)
        for file in files:
            port = file.replace(".txt", "")
            if port in includedPorts or extractMode == "1":
                with open(path + folder + "/" + file, "r", encoding="utf8") as txt:
                    for line in txt:
                        if line != "\n":
                            line = line.replace("\n", "")
                            if extractType == "1":
                                line = line + ":" + port
                            if extractType == "2":
                                line = line.split("|")
                                line[0] = line[0] + ":" + port
                                line = "|".join(line)
                            serverData.append(line)
                    txt.close()
    
    with open(outputFilename, "w", encoding="utf8") as txt:
        for line in serverData:
            txt.write(line + "\n")
        txt.close()
