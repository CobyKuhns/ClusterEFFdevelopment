import socket
import threading
import tkinter
import time
import datetime

#Establish our global variables
HOST = "135.134.128.16"
PORT = 40060

messageList = []
username = ""
closeProgram = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
global activeUsers
isChanged = False

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
    #Display the text box that shows the active users
    global activeUsers
    activeUsers = tkinter.Text(window, height = 10, width= 15)
    activeUsers.grid(row = 0, column= 1, pady = 2, padx = 5, sticky= "NE")
    #Set up the protocols to follow when someone exits the window
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()


def sendMessage(inputtxt):
    global isChanged
    #Get the current time so we can append the timestamp to messages
    now = datetime.datetime.now()
    now = now.strftime("%m/%d/%Y %I:%M%p")
    #Get the input text
    inp = inputtxt.get(1.0, "end-1c")
    #Send the text to the display box
    messageList.append(now + " " + username + ": " + inp)
    isChanged = True
    #Send the text to the server
    s.sendall(str.encode(inp))
    #Clear the box
    inputtxt.delete("1.0","end")

def receiveMessages(conn):
    global isChanged
    #This function runs continuously, checking for new messages
    while True:
        data = conn.recv(1024)
        data = data.decode("UTF_32", "ignore")
        identifier = data[0: 4]
        print(identifier)
        #Check for user list identifier
        if identifier == ":/UL":
            #send list to update active users function
            updateUserList(data[4:])
        else:
            messageList.append(data)
            isChanged = True
            print(data)
        

def updateUserList(userList):
    #Make the user list wait until the application is all started up
    time.sleep(.5)
    #Pull in the activeUsers textbox
    global activeUsers
    UserString = "Active Users:\n"
    #Parse through the userList received from the server
    splitList = userList.split(',')
    #Remove the blank item from the end
    splitList.pop()
    #Attach all users to a string
    for item in splitList:
        UserString = UserString + item + "\n"
    activeUsers.config(state= "normal")
    #Remove old user list and insert new
    activeUsers.delete(1.0,"end")
    activeUsers.insert(1.0, UserString)
    #Make sure user can't modify the textbox
    activeUsers.config(state= "disabled")
    # TESTING: print(UserString)
    # TESTING: print(splitList)

def namePrompt():
    #Set window properties and create window
    windowWidth = 200
    windowHeight = 50
    windowDimensions = "200x50"
    window = tkinter.Tk()
    window.title("")
    window.geometry(windowDimensions)
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    window.geometry("+{}+{}".format(posRight, posDown))
    #Label the textbox
    name = tkinter.Label(window, text="Name:").place(x=0, y=0)
    #Create the textbox to enter your name
    entry1 = tkinter.Entry(window)
    entry1.focus_set()
    entry1.pack()
    #Set enter key to send name to server and intiate main window
    window.bind('<Return>', lambda event, a=(entry1, window): nameSend(a))
    #Submit button process nameSend function when pressed.
    sbmitbtn = tkinter.Button(window, text = "Submit",command=lambda: nameSend((entry1, window)))
    sbmitbtn.pack()
    window.mainloop()

def nameSend(pair):
    #pair is a tuple comprised of the entrybox and the window object
    #grab the name from the entrybox
    name = pair[0].get()
    #pull in global username value
    global username
    username = name
    # TESTING: print(name)
    #Send username to server
    s.sendall(name.encode())
    #Destroy the window
    pair[1].destroy()

def printMessages(displaytxt):
    #This function basically just checks to see if the messageList has changed, and if it has, update the feed on screen
    global isChanged
    while True:
        if isChanged:
            text = ""
            for item in messageList:
                text = text + item
            isChanged = False
            displaytxt.config(state='normal')
            displaytxt.delete(1.0,"end")
            displaytxt.insert(1.0, text)
            displaytxt.config(state= 'disabled')
        time.sleep(.5)

def on_closing(window):
    #This function properly closes the connection to the server so that the server doesn't crash everytime someone leaves
    global closeProgram
    s.send("/exit".encode())
    s.close()
    window.destroy()

def main():
    #This function connects to the server and starts up the receivingMessages thread, then runs window()
    s.connect((HOST,PORT))
    t2 = threading.Thread(target=receiveMessages, args=(s,), daemon= True)
    t2.start()
    window()

if __name__ == "__main__":
    main()