#!/usr/bin/python3

#Paramiko package needs to be installed for usage of SSH from python
import paramiko
#this package allows the process to be put to sleep for a specified time interval
import time


def sendCommand(command):
    # Sends a cisco command to the SSH target, receives output, creates a file
    # sends output to the file and prints it to the screen. Then the file is closed
    remote_conn.send(command + "\n")
    time.sleep(2)
    output = remote_conn.recv(9999999)
    output = str(output, 'utf-8')
    print(output)
    fh = open(Hostname, "w")
    fh.write(output)
    fh.close()

#Try to open a file and retrive username and password
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

except Exception as e:
    print('No username and password file found!\n\nTo use this feature, create a file in the same directory named named_words.txt')
    print('first line: ip address\nsecond line: username\nthirdline: password\nfourth line: enable password')
    raise e

#This is a legacy countdown function. I thought it would be cool for the program
#to count down before running. It became tedious to watch.
counter = 0

#I discovered it takes time to receive output from the SSH target after
#commands are sent. This causes to program to wait for some interval before
#moving to the next operation. If you don't wait to receive the output, it will
#be truncated in your text file
sleep_interval = .6

#This message lets the user know the program is running and launches the counter
print("\n\nProgram running, hello Daryl...............")
while counter > -1: 
        print("Initiating connection to network device......" + str(counter))
        time.sleep(sleep_interval)
        counter = counter - 1
    
#This block of code initializes and lanunches the SSH session based on vaiables
#input from above 
remote_conn_pre=paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(
                        ip,
                        port=22,
                        username=username,  
                        password=password,
                        look_for_keys=False, 
                        allow_agent=False, 
                        timeout=100
                        )

#Did SSH connection succeed? Tell the user if the connection was successful
ConnectionStatus = remote_conn_pre.get_transport().is_active()
if ConnectionStatus == True:
    print("\n\nConnection SUCCESSFUL!!! Running show commands..............\n\n")
else:
    print("\n\nConnection FAILED!!!!\n\n")
        
#Create a shell object and handle for that shell
remote_conn = remote_conn_pre.invoke_shell()
output = remote_conn.recv(65535)

#Set terminal length of router output to 0. If this command is not run, router
#output is paused and waits for user input before continuing
remote_conn.send("terminal length 0\n")
time.sleep(sleep_interval)
output = remote_conn.recv(9999999)
output = str(output, 'utf-8')
print(output)


#prompts the SSH target for its hostname, sanitizes the returned information
#and holds the hostname in a variable to make a file name for the configuration file
remote_conn.send("\n")
time.sleep(sleep_interval)
output = remote_conn.recv(9999999)
output = str(output, 'utf-8')
output = output.replace('#','')
output = output.replace('>','')
output = output.replace('\r','')
output = output.replace('\n','')


#Create a new file name string based on the hostname of the SSH target.
Hostname = output + ".txt"


#Prompts SSH target for privlege exec mode
remote_conn.send("enable\n")
time.sleep(sleep_interval)
output = remote_conn.recv(9999999)
output = str(output, 'utf-8')
print(output)

#inputs the enable password and hit enter
remote_conn.send(enable_password + "\n")
time.sleep(sleep_interval)
output = remote_conn.recv(9999999)
output = str(output, 'utf-8')
print(output)

#Sends a cisco command to the SSH target, receives output, creates a file
#sends output to the file and prints it to the screen. Then the file is closed
remote_conn.send("show run\n")
time.sleep(5)
output = remote_conn.recv(9999999)
output = str(output, 'utf-8')
print(output)
fh = open(Hostname, "w")
fh.write(output)
fh.close()

#Sends a cisco command to the SSH target, receives output, creates a file
#sends output to the file and prints it to the screen. Then the file is closed
remote_conn.send("show ip arp\n")
time.sleep(5)
output = remote_conn.recv(9999999)
output = str(output, 'utf-8')
print(output)
fh = open(Hostname, "a")
fh.write(output)
fh.close()

#change the terminal lenght back to its default value
remote_conn.send("terminal length 40\n")
time.sleep(sleep_interval)
output = remote_conn.recv(65535)
output = str(output, 'utf-8')
print(output)

#Exit the router or switch
remote_conn.send("exit\n")
time.sleep(sleep_interval)
output = remote_conn.recv(65535)
output = str(output, 'utf-8')
print(output)

#Tell the user the program is complete
print("\n\nProgram complete, goodbye. I hope to see you soon!")
