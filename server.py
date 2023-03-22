import pickle
import socket
import sys
import threading
import time

#define Constants values used later 
HEADER = 64
SERVER_IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT!"
#allowed number of clients.
NUM_OF_CLIENTS=int(sys.argv[2])
#duration for report
SLEEP=int(sys.argv[3])

#Shared dict memory for client handling threads to use to store their messages
Clients={}
#establish the socket for the client (socket.AF_INET, socket.SOCK_STREAM) for TCP Connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#start connection between server and client
server.bind(ADDR)

#function runs in its own thread to handle each client
def handle_client(conn, addr,id):
    print(f"[NEW CONNECTION] {addr}")
    connected = True
    #sends sleep time to the client
    conn.send(str(SLEEP).encode(FORMAT))
    #count=1
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            message=pickle.loads(conn.recv(msg_length))
            if message == DISCONNECT_MESSAGE:
                connected = False
                print("Client Number [{}] DISCONNECTED!".format(id))
            else:
                conn.send("Message received".encode(FORMAT))
                #count+=1
                Clients[id]=message
    Clients.pop(id)
    conn.close()

#prints all clients properties every slp time.
def timed_print(clients,slp):
    count=1
    while(True):
        if len(clients)>0:
            print("Report number:",count)
            #we copy the dict of clients into list to avoid multiple-access in the same time on dict.
            for client in list(clients):
                print("Client -",client,"Usage Info:")
                counter=0
                for cpu in (clients[client]["cpu"]):
                    counter+=1
                    print("CPU-",counter,":",cpu,"%")
                print("RAM:",clients[client]["ram"],"%")
                print("Disk:",clients[client]["disk"],"%")
                print("________________________")
            count+=1
            time.sleep(slp)

#function to run the server
def start_server():
    id=0
    server.listen(NUM_OF_CLIENTS)
    #Print the server IP and Port address
    print(f"[LISTENING] Server is listening on {SERVER_IP}")
    #start the printing thread
    threading.Thread(target=timed_print, args=(Clients, SLEEP)).start()
    
    while True:
        #check if max number of clients is reached
        if threading.active_count()-2 <NUM_OF_CLIENTS:
            #accept the client connection
            conn, addr = server.accept()
            #increment id by 1 to keep ids unique
            id+=1
            #start the client thread with the new information (connection , address , id)
            threading.Thread(target=handle_client, args=(conn, addr,id)).start()
            #prints the number of active connections
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
        else:
            #close client connection if max number of clients is reached
            conn, addr = server.accept()
            conn.close()

#start the server
print("[STARTING]...")
start_server()