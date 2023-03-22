import psutil
import socket
import pickle
import pytimedinput as bt

#define Constants values used later 
HEADER = 64
SERVER_IP = "127.0.0.1"
PORT =12345
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT!"


#establish the socket for the client (socket.AF_INET, socket.SOCK_STREAM) for TCP Connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#start connection between server and client
client.connect(ADDR)

#Check if Max Number of connections reached and quit if connection refused
try:
    SLEEP=int(client.recv(2048).decode(FORMAT))
except ValueError:
    print("Max Number of connections reached , try Later.")
    quit()

#function takes client's device properties and return it into dict
def device_properties():
    props={}
    props["cpu"]=psutil.cpu_percent(percpu=True,interval=1)
    props["ram"]=psutil.virtual_memory().percent
    props["disk"]=psutil.disk_usage("/").percent
    return props

#function to send message to server
def send(message):
    #convert message to byte
    byte_message=pickle.dumps(message)
    #calculate the converted byte message length
    msg_length = len(byte_message)
    #convert the msg_length to byte
    send_length = str(msg_length).encode(FORMAT)
    #create empty byte string of message length
    send_length += b' ' * (HEADER - len(send_length))
    #send the buffer 
    client.send(send_length)
    #send the message
    client.send(byte_message)
    #received message conformation from server 
    print(client.recv(2048).decode(FORMAT))

def start_client():
    #start the communication
    while(True):
        #keep sending properties
        send(device_properties())
        #stop the process of sending if client pressed the D key
        finished=bt.timedKey("if you want to disconnect press D: ",timeout=SLEEP,allowCharacters="dD",resetOnInput=False)
        if finished[0]=="d"or finished[0]=="D":
            break

start_client()
#send the Disconnect message to the server
send(DISCONNECT_MESSAGE)