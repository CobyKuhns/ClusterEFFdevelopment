import socket
import threading

HOST = "127.0.0.1"
PORT = 42069
connections = []
receivingThreads = []
messageQueue = []

def acceptConnections():
    #Makes sure we don't go over ten connections
    while len(connections) <= 10:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        name = conn.recv(1024)
        name = name.decode()
        connection = (name, conn)
        connections.append(connection)
        t1 = threading.Thread(target=receiveMessages, args=(connection,))
        receivingThreads.append(t1)
        # calls the last thread in the list
        receivingThreads[len(receivingThreads) - 1].start()
        messageQueue.append(("SERVER",  "{} has joined the ClusterFuck!\n".format(name)))


def receiveMessages(conn):
    while True:
        data = conn[1].recv(1024)
        if not data:
            messageQueue.append((conn[0], "Disconnected"))
            print("{}: Disconnected".format(conn[0]))
            conn[1].close()
            break
        else:
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
            data = messageQueue[0]
            print(data)
            message = "{}: {}".format(messageQueue[0][0],messageQueue[0][1])
            messageQueue.pop(0)
            for conn in connections:
                if not conn[0] == data[0]:
                    conn[1].send(message.encode())

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

def main():
    t1 = threading.Thread(target=sendMessages)
    t1.start()
    acceptConnections()


if __name__ == "__main__":
    main()