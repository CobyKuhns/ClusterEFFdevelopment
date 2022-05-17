import socket
import threading
import tkinter
import time
import datetime

HOST = "127.0.0.1"
PORT = 42069

messageList = []
username = ""
global closeProgram
closeProgram = False

def window():
    #Prompt the user for their name
    namePrompt()
    #create window and configure the settings
    window = tkinter.Tk()
    window.title("ClusterFuck")
    window.geometry("1000x700")
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    #create the message Display
    displaytxt = tkinter.Text(window, height=30, width=100)
    displaytxt.pack()
    #Start the thread that handles message reception
    messageThread = threading.Thread(target=printMessages, args=(displaytxt,), daemon=True)
    messageThread.start()
    #Make sure the user can't edit the display textbox
    displaytxt.config(state= 'disabled')
    #Create the input text box
    inputtxt = tkinter.Text(window, height=5, width=100)
    inputtxt.pack()
    #bind enter to the sendMessage function
    window.bind('<Return>', lambda event, a=inputtxt: sendMessage(a))
    #Create button to send messages
    sendButton = tkinter.Button(window, text="Send", command=lambda: sendMessage(inputtxt))
    sendButton.pack()
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()


def sendMessage(inputtxt):
    now = datetime.datetime.now()
    now = now.strftime("%m/%d/%Y %H:%M:%S")
    inp = inputtxt.get(1.0, "end-1c")
    messageList.append(now + " " + username + ": " + inp)
    s.sendall(str.encode(inp))
    inputtxt.delete("1.0","end")

def receiveMessages(conn):
    while True:
        data = conn.recv(1024)
        messageList.append(data.decode())
        print(data.decode())

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
    name = entry1[0].get()
    global username
    username = name
    print(name)
    s.sendall(name.encode())
    entry1[1].destroy()

def printMessages(displaytxt):
    while True:
        text = ""
        if messageList:
            for item in messageList:
                text = text + item
            displaytxt.config(state='normal')
            displaytxt.delete(1.0,"end")
            displaytxt.insert(1.0, text)
            displaytxt.config(state= 'disabled')
        time.sleep(1)

def on_closing(window):
    global closeProgram
    s.send("/exit".encode())
    s.close()
    closeProgram = True
    window.destroy()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
t1 = threading.Thread(target=window, daemon= True)
t1.start()
t2 = threading.Thread(target=receiveMessages, args=(s,), daemon= True)
t2.start()
while not closeProgram:
    pass

