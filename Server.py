import socket
import threading
import datetime
import os
import sys

#Setting Global Variables
connections = []
receivingThreads = []
messageQueue = []

def acceptConnections():
    hostPair = []
    i = 0
    #This section opens the settings file and reads the values set for host and port
    with open(os.path.join(sys.path[0], "SETTINGS.txt"), "r") as f:
        for line in f:
            splitLine = line.split("=")
            if i == 0:
                splitLine[1] = splitLine[1].rstrip(splitLine[1][-1])
                hostPair.append(splitLine[1])
            else:
                hostPair.append(int(splitLine[1]))
            print(splitLine)
            i += 1
    HOST = hostPair[0]
    PORT = hostPair[1]
    #Makes sure we don't go over ten connections
    while True:
        if len(connections) < 10:
            #Sets up socket for client
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen()
            #Sets socket to variables and receives username from client
            conn, addr = s.accept()
            name = conn.recv(1024)
            name = name.decode("UTF_32")
            #Makes a tuple from the connection and username, and appends this to the connections list
            connection = (name, conn)
            connections.append(connection)
            #Sends user list to all clients
            sendUserList()
            #Creates a message receiving thread for the connection in question, and adds it to the thread list
            t1 = threading.Thread(target=receiveMessages, args=(connection,))
            receivingThreads.append(t1)
            # calls the last thread in the list
            receivingThreads[len(receivingThreads) - 1].start()
            #Sends an update to all members in chat
            messageQueue.append(("SERVER",  "{} has joined the ClusterEFF. Welcome!\n".format(name)))


def receiveMessages(conn):
    while True:
        #Receive message
        data = conn[1].recv(1024)
        if not data:
            messageQueue.append((conn[0], "Disconnected"))
            print("{}: Disconnected".format(conn[0]))
            conn[1].close()
            break
        else:
            #decode the message and check if its a special case
            message = data.decode("UTF_32")
            if message[:3] == "/pm":
                #if its a privateMessage, try to send it, and tell the sender if the receiver cant be found
                if not privateMessage(conn[0], message):
                    conn[1].send("ERROR: USER NOT FOUND".encode())
            elif message == "/exit":
                #If its an exit command, close the connection and remove it from the list of currentConnections
                conn[1].close()
                print("{} disconnected".format(conn[0]))
                removeConnection(conn[1])
                messageQueue.append((conn[0], "Disconnected\n"))
                break
            else:
                print("{}: {}".format(conn[0],message))
                messageQueue.append((conn[0], message))

def sendMessages():
    #This function just runs through the message queue and sends everything it finds to the clients
    while True:
        if messageQueue:
            now = datetime.datetime.now()
            now = now.strftime("%m/%d/%Y %I:%M%p")
            data = messageQueue[0]
            print(data)
            message = "{} {}: {}".format(now, messageQueue[0][0],messageQueue[0][1])
            messageQueue.pop(0)
            for conn in connections:
                if not conn[0] == data[0]:
                    conn[1].send(message.encode("UTF_32"))

def sendUserList():
    #sends the UserList as a string separated by commas, and appends a special identifier to the front of the message
    userList = ":/UL"
    for conn in connections:
        userList = userList + conn[0] + ','
    for conn in connections:
        conn[1].sendall(userList.encode("UTF_32"))
        
def privateMessage(name, message):
    userFound = False
    #Splits up the input message
    parse = message.split()
    #finds the username of the recipient
    user = parse[1]
    #Then removes the command and username from the list
    parse.pop(0)
    parse.pop(0)
    #Makes the message a string again
    message = " ".join(parse)
    #Then properly formats the string
    packet = ("PM from {}: {}".format(name, message))
    #Finds the right connection and then sends the message
    for conn in connections:
        if conn[0] == user:
            conn[1].send(packet.encode())
            userFound = True
    #Function returns whether the user was found or not
    return userFound

def removeConnection(name):
    #This function removes the name connection from the list
    for connection in connections:
        if connection[1] == name:
            connections.remove(connection)
    sendUserList()
    

def main():
    #Starts the sendMessages thread and moves to the acceptConnections thread
    t1 = threading.Thread(target=sendMessages)
    t1.start()
    acceptConnections()


if __name__ == "__main__":
    main()