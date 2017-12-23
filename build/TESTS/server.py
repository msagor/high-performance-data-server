import sys
import socket
import database
import unit_tests
print "given args: " + str(sys.argv)

RESERVED_WORDS = ["all", "append", "as", "change", "create", "default", "delegate", "delegation", "delegator", "delete", "do", "exit", "foreach", "in", "local", "password", "principal", "read", "reaplacewith", "return", "set", "to", "write", "***"]
RESERVED_EXTRA_WORDS = ["split", "concat", "tolower", "notequal", "equal", "filtereach", "with", "let"]





if len(sys.argv) == 1:
	# perform tests for database
	unit_tests.UNIT_TESTS()



###### PORT HANDLING
if len(sys.argv) != 2 and len(sys.argv) != 3:
	print "invalid argument length given. shutting down. "
	print "usage: python server.py PORT [PASSWORD] "
	exit(1)
if not sys.argv[1].isdigit():
	print "given port argument is not an integer. shutting down. "
	exit(1)
SRV_PORT = int(sys.argv[1])
if SRV_PORT < 1024 or SRV_PORT > 65535:
	print "given port is out of acceptable range. shutting down. "
	exit(1)



###### PASSWORD HANDLING
SRV_PASSWORD = "admin"
if len(sys.argv) == 3:
	SRV_PASSWORD = sys.argv[2]

print "RESULT: server port(" + str(SRV_PORT) + ") server password(" + SRV_PASSWORD + ")"


###### INITIALIZE GLOBAL VARIABLE DATABASE
VAR_DATABASE = database.VARIABLE_DB()


###### INITIALIZE GLOBAL USER DATABASE, ADD ADMIN
USER_DATABASE = database.USER_DB()
USER_DATABASE.create_user("admin", "admin", SRV_PASSWORD)


###### CONNECTION HANDLING FOR CLIENTS (RECV THE REQUESTED CODE TO EXECUTE)
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SRV_ADDRESS = ('localhost', SRV_PORT)
SOCKET.bind(SRV_ADDRESS)

print "starting server... please wait"

SOCKET.listen(1)

server_alive = True

while server_alive:
	# wait for a connection
	try:
		print "waiting for a connection... "
		SRV_CONNECTION, CLIENT_ADDR = SOCKET.accept()
		terminating_code = "***\n"

		print "connection established from address " + str(CLIENT_ADDR)
		input_program = ""
		while server_alive:

			data = SRV_CONNECTION.recv(2048)

			if data:
				#print "GOT THE FOLLOWING INFORMATION:  \n|" + str(data) + "|"
				print str(data)
				input_program += data
				if data == "***" or data == "***\n":
					break
			else:
				print "No more data from " + str(CLIENT_ADDR)
				break

		print "the following program was received: \n" + str(input_program)

		print "Network recv complete."

        #################################################
        ########## PROCESS REQUEST INFORMATION HERE #####




        #################################################
        ########## PROCESS REQUEST INFORMATION HERE #####

		if input_program == "":
			print "A problem with receiving the program occurred. "
			exit(1)

		print "request fulfilled. "
		break # TODO delete this break statement at a later time
	except KeyboardInterrupt:
		print "\nkeyboard interrupt detected. exiting... "
		exit(0)

print "server exiting. have a good day. "
exit(0)