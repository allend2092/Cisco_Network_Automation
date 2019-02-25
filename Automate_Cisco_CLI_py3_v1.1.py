#!/usr/bin/python3

#Paramiko package needs to be installed for usage of SSH from python
import paramiko
#this package allows the process to be put to sleep for a specified time interval
import time

#Sends a cisco command to the SSH target, receives output, creates a file
#sends output to the file and prints it to the screen. Then the file is closed
def sendCommand(command, remote_conn, sleep_interval, hostname):
    # Sends a cisco command to the SSH target, receives output, creates a file
    # sends output to the file and prints it to the screen. Then the file is closed
    remote_conn.send(command + "\n")
    time.sleep(sleep_interval)
    output = remote_conn.recv(9999999)
    output = str(output, 'utf-8')
    print(output)
    fh = open(hostname, "a")
    fh.write(output)
    fh.close()

def setTerminalLenth(number, remote_conn, sleep_interval):
    # Set terminal length of router output to 0. If this command is not run, router
    # output is paused and waits for user input before continuing
    remote_conn.send("terminal length " + number + "\n")
    time.sleep(sleep_interval)
    output = remote_conn.recv(9999999)
    output = str(output, 'utf-8')
    print(output)

def getHostname(remote_conn, sleep_interval):
    # prompts the SSH target for its hostname, sanitizes the returned information
    # and holds the hostname in a variable to make a file name for the configuration file
    remote_conn.send("\n")
    time.sleep(sleep_interval)
    output = remote_conn.recv(9999999)
    output = str(output, 'utf-8')
    output = output.replace('#', '')
    output = output.replace('>', '')
    output = output.replace('\r', '')
    output = output.replace('\n', '')
    fh = open(output + '.txt', "w")
    fh.close()
    return output + ".txt"

def endProgram(remote_conn, sleep_interval):
    # Exit the router or switch
    remote_conn.send("exit\n")
    time.sleep(sleep_interval)
    output = remote_conn.recv(65535)
    output = str(output, 'utf-8')
    print(output)

    # Tell the user the program is complete
    print("\n\nProgram complete, goodbye. I hope to see you soon!")


def promptForEnablePassword(remote_conn, sleep_interval):
    # Prompts SSH target for privlege exec mode
    remote_conn.send("enable\n")
    time.sleep(sleep_interval)
    output = remote_conn.recv(9999999)
    output = str(output, 'utf-8')
    print(output)

def sendEnablePassword(remote_conn, sleep_interval, enable_password):
    # inputs the enable password and hit enter
    remote_conn.send(enable_password + "\n")
    time.sleep(sleep_interval)
    output = remote_conn.recv(9999999)
    output = str(output, 'utf-8')
    print(output)

def getLoginCredentials():
    # Try to open a file and retrive username and password
    try:
        fh = open('names_words.txt', 'r')
        ip = fh.readline()
        username = fh.readline()
        password = fh.readline()
        enable_password = fh.readline()

        ip = ip.rstrip()
        username = username.rstrip()
        password = password.rstrip()
        enable_password = enable_password.rstrip()

        loginCredentials = ['success', ip, username, password, enable_password]

        return loginCredentials


    except Exception as e:
        error_msg1 = 'No username and password file found!\n\nTo use this feature, create a file in the same directory named named_words.txt'
        error_msg2 = 'first line: ip address\nsecond line: username\nthirdline: password\nfourth line: enable password'
        loginCredentials = ["failed", error_msg1, error_msg2, "", ""]
        return loginCredentials


def connectToRemoteDevice(counter, ip,username,password):
    # This message lets the user know the program is running and launches the counter
    print("\n\nProgram running, hello user...............")
    while counter > -1:
        print("Initiating connection to network device......" + str(counter))
        time.sleep(sleep_interval)
        counter = counter - 1

        # This block of code initializes and launches the SSH session
        remote_conn_pre = paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection = remote_conn_pre.connect(
            ip,
            port=22,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=100
        )

        # Did SSH connection succeed? Tell the user if the connection was successful
        ConnectionStatus = remote_conn_pre.get_transport().is_active()
        if ConnectionStatus == True:
            print("\n\nConnection SUCCESSFUL!!! Running CLI commands to network device...\n\n")
        else:
            print("\n\nConnection FAILED!!!!\n\n")

    # Create a shell object and handle for that shell
    remote_conn = remote_conn_pre.invoke_shell()
    return remote_conn

def validateLoginCredentials(loginCredentials):
    # Check if we successfully retrieved the username and password from a file
    # If there is no file, exit program and throw error
    if loginCredentials[0] == 'failed':
        print(loginCredentials[1])
        print(loginCredentials[2])
        exit()
    elif loginCredentials[0] == 'success':
        return

#####################################################################################################
#####################################################################################################


#This is a legacy countdown function. I thought it would be cool for the program
#to count down before running. It became tedious to watch.
counter = 0

#Pauses program to wait for output from connected device. You can wait more or less time here.
sleep_interval = 1.5

#Get login Credentials
loginCredentials = getLoginCredentials()

#Check if login credentials were sucessfully retrived from the file names_words.txt
validateLoginCredentials(loginCredentials)

#Establish connection to remote device
remote_conn = connectToRemoteDevice(counter, ip = loginCredentials[1],username = loginCredentials[2],password = loginCredentials[3])

#set terminal length to zero. This allows program to receive output without need for sending carraige returns
setTerminalLenth('0', remote_conn, sleep_interval)

#Create / overwrite file and hostname with name based on the hostname of the SSH target.
hostname = getHostname(remote_conn, sleep_interval)

#Send Commands To device and received output on screen and in a textfile
promptForEnablePassword(remote_conn, sleep_interval)
sendEnablePassword(remote_conn, sleep_interval, enable_password = loginCredentials[4])
sendCommand('show run', remote_conn, sleep_interval, hostname)
sendCommand('show ip arp', remote_conn, sleep_interval, hostname)
setTerminalLenth('40', remote_conn, sleep_interval)
endProgram(remote_conn, sleep_interval)

