import socket
import threading
import datetime

HOST = "192.168.5.97"
PORT = 42069
connections = []
receivingThreads = []
messageQueue = []

def acceptConnections():
    #Makes sure we don't go over ten connections
    while len(connections) <= 10:
        #Sets up socket for client
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        #Sets socket to variables and receives username from client
        conn, addr = s.accept()
        name = conn.recv(1024)
        name = name.decode()
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
            #decode the
            message = data.decode()
            if message[:3] == "/pm":
                if not privateMessage(conn[0], message):
                    conn[1].send("ERROR: USER NOT FOUND".encode())
            elif message == "/exit":
                conn[1].close()
                print("{} disconnected".format(conn[0]))
                removeConnection(conn[1])
                messageQueue.append((conn[0], "Disconnected\n"))
                break
            else:
                print("{}: {}".format(conn[0],message))
                messageQueue.append((conn[0], message))

def sendMessages():
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
                    conn[1].send(message.encode())

def sendUserList():
    userList = ":/UL"
    for conn in connections:
        userList = userList + conn[0] + ','
    for conn in connections:
        conn[1].sendall(userList.encode())
        
def privateMessage(name, message):
    userFound = False
    parse = message.split()
    user = parse[1]
    parse.pop(0)
    parse.pop(0)
    message = " ".join(parse)
    packet = ("PM from {}: {}".format(name, message))
    for conn in connections:
        if conn[0] == user:
            conn[1].send(packet.encode())
            userFound = True
    return userFound

def removeConnection(name):
    for connection in connections:
        if connection[1] == name:
            connections.remove(connection)
    sendUserList()
    

def main():
    t1 = threading.Thread(target=sendMessages)
    t1.start()
    acceptConnections()


if __name__ == "__main__":
    main()