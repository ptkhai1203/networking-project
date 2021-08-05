from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from functools import partial
from tkinter import messagebox
import tkinter
import time

def receive():
    """Handles receiving of messages"""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
        except OSError:
            break
        except:
            msg_list.insert(tkinter.END, 'Server disconnected')
            time.sleep(5)
            client_socket.close()
            top.quit()
            break
        for ms in msg.split('\n'):
            msg_list.insert(tkinter.END, ms)

def send(event = None):  # event is passed by binders
    """Handles sending of messages"""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field
    try:
        client_socket.send(bytes(msg, "utf8"))
    except:
        print('Server disconnected. This application will close after 5 seconds')
        time.sleep(5)
        client_socket.close()
        top.quit()
    if msg == "{quit}":
        client_socket.close()
        top.quit()

def on_closing(event = None):
    """This function is to be called when the window is closed"""
    my_msg.set("{quit}")
    send()

def validateLogin(username, password):
    msg = username.get()
    username.set("")
    try:
        client_socket.send(bytes(msg + ' 1', "utf8"))
    except:
        client_socket.close()
        tkWindow.destroy()
        return
    msg = password.get()
    password.set("")
    try:
        client_socket.send(bytes(msg, "utf8"))
    except:
        client_socket.close()
        tkWindow.destroy()
        return
    global status_login
    status_login = client_socket.recv(BUFSIZ).decode("utf8")
    if status_login == "success":
        messagebox.showinfo("", "Login successfully")
        tkWindow.destroy()
    elif status_login == "unsuccess":
        messagebox.showinfo("", "Your username or password is incorrect")
        status_login = "success"

def validateRegister(username, password):
    msg = username.get()
    username.set("")
    try:
        client_socket.send(bytes(msg + ' 2', "utf8"))
    except:
        client_socket.close()
        tkWindow.destroy()
        return
    msg = password.get()
    password.set("")
    try:
        client_socket.send(bytes(msg, "utf8"))
    except:
        client_socket.close()
        tkWindow.destroy()
        return
    global status_regis
    status_regis = client_socket.recv(BUFSIZ).decode("utf8")
    if status_regis == "success":
        messagebox.showinfo("", "Register successfully")
        tkWindow.destroy()
    elif status_regis == "unsuccess":
        messagebox.showinfo("", "Your username is already existed")
        status_regis = "success"

# ----Now comes the sockets part----
HOST = input('Enter host: ')
PORT = 33000
BUFSIZ = 1024 * 4
ADDR = (HOST, PORT)
status_login = "success"
status_regis = "success"

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

tkWindow = tkinter.Tk()
tkWindow.geometry('400x150')
tkWindow.title('Login Application')

usernameLabel = tkinter.Label(tkWindow, text = "Username").grid(row = 0, column = 0)
username = tkinter.StringVar()
usernameEntry = tkinter.Entry(tkWindow, textvariable = username).grid(row = 0, column = 1)

passwordLabel = tkinter.Label(tkWindow,text = "Password").grid(row = 1, column = 0)
password = tkinter.StringVar()
passwordEntry = tkinter.Entry(tkWindow, textvariable = password, show = '*').grid(row = 1, column = 1)

validateLogin = partial(validateLogin, username, password)
validateRegister = partial(validateRegister, username, password)

loginButton = tkinter.Button(tkWindow, text = "Login", command = validateLogin).grid(row = 4, column = 0)
regisButton = tkinter.Button(tkWindow, text = "Register", command = validateRegister).grid(row = 4, column = 1)

tkWindow.mainloop()

while status_login != "success":
    usernameEntry = tkinter.Entry(tkWindow, textvariable = username).grid(row = 0, column = 1)
    passwordEntry = tkinter.Entry(tkWindow, textvariable = password, show = '*').grid(row = 1, column = 1)
    loginButton = tkinter.Button(tkWindow, text = "Login", command = validateLogin).grid(row = 4, column = 0)

while status_regis != "success":
    usernameEntry = tkinter.Entry(tkWindow, textvariable = username).grid(row = 0, column = 1)
    passwordEntry = tkinter.Entry(tkWindow, textvariable = password, show = '*').grid(row = 1, column = 1)
    regisButton = tkinter.Button(tkWindow, text = "Register", command = validateRegister).grid(row = 4, column = 11)

top = tkinter.Tk()
top.title("Get COVID application")
top.geometry('600x625')

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages

# Following will contain the messages
msg_list = tkinter.Listbox(messages_frame, height = 35, width = 125, yscrollcommand = scrollbar.set)
scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
msg_list.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable = my_msg)
entry_field.bind("<Return>", send)
entry_field.pack(fill = tkinter.BOTH, expand = True)
send_button = tkinter.Button(top, text = "Send", command = send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

receive_thread = Thread(target = receive)
receive_thread.start()
tkinter.mainloop()