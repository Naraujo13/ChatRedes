import socket, select
 
#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    i = -1
    for nickname, socket in CONNECTION_LIST.items():
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                del CONNECTION_LIST.keys()[CONNECTION_LIST.values().index(socket)]


def broadcast_pm(sock, message):
    # Do not send the message to master socket and the client who has send us the message
    for nickname, socket in CONNECTION_LIST.items():
        if socket == sock:
            try:
                socket.send(message)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                del CONNECTION_LIST.keys()[CONNECTION_LIST.values().index(socket)]


if __name__ == "__main__":
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = {}
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST['server'] = server_socket
 
    print "Chat server started on port " + str(PORT)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST.values(),[],[])
 
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                nickname = sockfd.recv(RECV_BUFFER)
                CONNECTION_LIST[nickname] = sockfd
                print "Client (%s, %s) connected" % addr
                print "Nickname: " + nickname
                broadcast_data(sockfd, "\r" + nickname + " entered the room!\n")
             
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    sender = CONNECTION_LIST.keys()[CONNECTION_LIST.values().index(sock)]
                    if '/' not in data :
                        broadcast_data(sock, "\r" + sender + ": " +  data)
                    else:
                        if data == "/list\n":
                            message = "Users in the room:\n"
                            for nickname in CONNECTION_LIST.keys():
                                if nickname != "server":
                                    message += nickname + "; "
                            broadcast_pm(sock, "\r" + message + "\n")
                        elif data == "/quit\n":
                            broadcast_data(sock, "\r" + sender + " has left the room!\n")
                            print "Client (%s, %s) disconnected.\n" % addr
                            sock.close()
                            del CONNECTION_LIST[sender]
                        else:
                            nickname = data.split(" ")
                            nickname = nickname[0].replace("/", "")
                            try:
                                broadcast_pm(CONNECTION_LIST[nickname], "\r\n[PM]" + sender + ": " + data.replace("/" + nickname + " ", "") + "\n")
                            except:
                                broadcast_pm(sock, "\rUser not found!\n")
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    del CONNECTION_LIST.keys()[CONNECTION_LIST.values().index(sock)]
                    continue
     
    server_socket.close()
