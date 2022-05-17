import socket
import threading
import tkinter
import time
import datetime

HOST = "192.168.5.97"
PORT = 42069

messageList = []
username = ""
global closeProgram
closeProgram = False
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
global activeUsers

def window():
    #Prompt the user for their name
    namePrompt()
    #create window and configure the settings
    window = tkinter.Tk()
    window.title("ClusterEFF")
    window.geometry("950x580")
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    #create the message Display
    displaytxt = tkinter.Text(window, height=30, width=100)
    displaytxt.grid(row= 0, column= 0, pady =2, padx = 2)
    #Start the thread that handles message reception
    messageThread = threading.Thread(target=printMessages, args=(displaytxt,), daemon=True)
    messageThread.start()
    #Make sure the user can't edit the display textbox
    displaytxt.config(state= 'disabled')
    #Create the input text box
    inputtxt = tkinter.Text(window, height=5, width=100)
    inputtxt.grid(row= 1, column= 0, pady =2, padx = 2)
    #bind enter to the sendMessage function
    window.bind('<Return>', lambda event, a=inputtxt: sendMessage(a))
    #Create button to send messages
    sendButton = tkinter.Button(window, text="Send", command=lambda: sendMessage(inputtxt))
    sendButton.grid(row= 1, column= 1, pady =2, sticky= "W")
    global activeUsers
    activeUsers = tkinter.Text(window, height = 10, width= 15)
    activeUsers.grid(row = 0, column= 1, pady = 2, padx = 5, sticky= "NE")
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()


def sendMessage(inputtxt):
    now = datetime.datetime.now()
    now = now.strftime("%m/%d/%Y %I:%M%p")
    inp = inputtxt.get(1.0, "end-1c")
    messageList.append(now + " " + username + ": " + inp)
    s.sendall(str.encode(inp))
    inputtxt.delete("1.0","end")

def receiveMessages(conn):
    while True:
        data = conn.recv(1024)
        data = data.decode()
        identifier = data[0: 4]
        print(identifier)
        #Check for user list identifier
        if identifier == ":/UL":
            #send list to update active users function
            updateUserList(data[4:])
        else:
            messageList.append(data)
            print(data)
        

def updateUserList(userList):
    time.sleep(.5)
    global activeUsers
    UserString = "Active Users:\n"
    splitList = userList.split(',')
    splitList.pop()
    for item in splitList:
        UserString = UserString + item + "\n"
    activeUsers.config(state= "normal")
    activeUsers.delete(1.0,"end")
    activeUsers.insert(1.0, UserString)
    activeUsers.config(state= "disabled")
    print(UserString)

    print(splitList)

def namePrompt():
    windowWidth = 200
    windowHeight = 50
    windowDimensions = "200x50"
    window = tkinter.Tk()
    window.title("")
    window.geometry(windowDimensions)
    name = tkinter.Label(window, text="Name:").place(x=0, y=0)
    entry1 = tkinter.Entry(window)
    entry1.focus_set()
    entry1.pack()
    window.bind('<Return>', lambda event, a=(entry1, window): nameSend(a))
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    window.geometry("+{}+{}".format(posRight, posDown))
    sbmitbtn = tkinter.Button(window, text = "Submit",command=lambda: nameSend((entry1, window)))
    sbmitbtn.pack()
    window.mainloop()

def nameSend(entry1):
    global s
    name = entry1[0].get()
    global username
    username = name
    print(name)
    s.sendall(name.encode())
    entry1[1].destroy()

def printMessages(displaytxt):
    messageListCompare = []
    while True:
        text = ""
        if messageList:
            for item in messageList:
                text = text + item
        messageListCompare = messageList
        displaytxt.config(state='normal')
        displaytxt.delete(1.0,"end")
        displaytxt.insert(1.0, text)
        displaytxt.config(state= 'disabled')
        time.sleep(.5)

def on_closing(window):
    global closeProgram
    s.send("/exit".encode())
    s.close()
    closeProgram = True
    window.destroy()

def main():
    s.connect((HOST,PORT))
    t2 = threading.Thread(target=receiveMessages, args=(s,), daemon= True)
    t2.start()
    window()

if __name__ == "__main__":
    main()