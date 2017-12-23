# SECURITY-PROJECT: Secure Data Server
**Project for CSCE 689: Software Security**. The goal of this project is to implement a security-conscious data server. Clients can connect to the server one-at-a-time via TCP and send a textual program. The server executes the program, sends textual output back to the client, and disconnects. Executing a program may cause data to be stored on the server, which can be accessed later by other programs as long as the server remains running. Data does not persist once the server stops running.

## Build-It Round
When our server receives a program from a client, it will first tokenize received input. During this step, our server checks for syntax violations, returning "FAILED" if any are found. Following syntax checking, the server then checks for valid user/variable authorization, returning "DENIED" if any are found. Once these checks are passed, the server then performs the operations specified in the client's input program, accessing the USER_DB and VARIABLE_DB databases as needed. Finally, once the server reaches the end of the received program, it generates the proper response ("SUCCESS: ...", "FAILED", "DENIED", etc.) and sends this back to the client.

### Component Diagram
![bibifi-diagram](https://github.tamu.edu/storage/user/1307/files/e6e3fdf6-bcc7-11e7-816e-43edf9532bc4)

