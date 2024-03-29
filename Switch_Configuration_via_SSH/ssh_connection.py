import paramiko
import os.path
import time
import sys 
import re

#Checking username/password file
#Prompting user for input - USERNAME/PASSWORD FILE
user_file = input("\n# Enter user file path and name (e.g. /Users/stevenwilliams/NetworkApplications/Switch_Configuration_via_SSH/user.txt): ")

#Verifying the validity of the USERNAME/PASSWORD file
if os.path.isfile(user_file) == True:
	print("\n * Username/password file is valid. \n")

else:
	print("\n* File {} does not exist. Please check and try again.\n".format(user_file))
	sys.exit()

#Checking commands file
#Prompting user for input - COMMANDS FILE
cmd_file = input("\n# Enter commands file path name (e.g. /Users/stevenwilliams/NetworkApplications/Switch_Configuration_via_SSH/cmd.txt): ")

#Verifying the validity of the COMMANDS FILE
if os.path.isfile(cmd_file) == True:
	print("\n* Command file is valid.\n")

else:
	print("\n* File {} does not exist. Please check and try again.\n".format(cmd_file))
	sys.exit()

#Open SSHv2 connection to the device
def ssh_connection(ip):

	global user_file
	global cmd_file

	#Creating SSH Connection
	try:
		#Define SSH parameters
		selected_user_file = open(user_file, 'r')

		#Starting from the beginning of the file
		selected_user_file.seek(0)

		#Reading the username from the file
		username = selected_user_file.readlines()[0].split(',')[0].rstrip("\n")

		#Starting from the beginning of the file
		selected_user_file.seek(0)

		#Reading the password from the file
		password = selected_user_file.readlines()[0].split(',')[1].rstrip("\n")

		#Logging into device 
		session = paramiko.SSHClient()

		#For testing purposes, this allow auto-accepting unknown hohst keys
		#Not to be used in production. This default would be RejectPolicy
		session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		#Connect to the device using username and password
		session.connect(ip.rstrip("\n"),username = username, password = password)

		#Start an interactive shell using username and password
		connection = session.invoke_shell()

		#Setting terminal length for entire output - disable pagination
		connection.send("enable\n")
		connection.send("terminal length 0\n")
		time.sleep(1)

		#Entering global configuration mode
		connection.send("\n")
		connection.send("configure terminal\n")
		time.sleep(1)

		#Open user selected file for reading
		selected_cmd_file = open(cmd_file, 'r')

		#Starting from the beginning of the file
		selected_cmd_file.seek(0)

		for each_line in selected_cmd_file.readlines():
			connection.send(each_line + '\n')
			time.sleep(2)

		#Closing the user file
		selected_user_file.close()

		#Closing the command file
		selected_cmd_file.close()

		#Checking command output for IOS syntax errors
		router_output = connection.recv(65535)

		if re.search(b"% Invalid input", router_output):
			print("* There was at least one IOS syntax error on device {} :".format(ip))

		else:
			print("\nDone for device {}\n".format(ip))

		#Test for reading command output
		print(str(router_output) + "\n")
		
		#Extract IP address only from command output
		#print(re.findall(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", str(router_output))[1])


		#Closing the connection
		session.close()

	except paramiko.AuthenticationException:
		print("* Invalid username or password\n * Please check the username/password file or the device configuration.")
		print("* Closing program...")