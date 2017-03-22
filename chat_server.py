imPort socket, select
 
# Função public_message:
#
# Envia uma mensagem publica para todos os usuários conectados na sala
# ignorando o socket do servidor e do usuário que enviou a mensagem

def public_message (sock, message):
    for nickname, socket in Connected_Sockets.items():
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                socket.close()
                del Connected_Sockets.keys()[Connected_Sockets.values().index(socket)]


# Função private_message:
#
# Envia uma mensagem privada para um usuário conectado na sala

def private_message(sock, message):
    for nickname, socket in Connected_Sockets.items():
        if socket == sock:
            try:
                socket.send(message)
            except:
                socket.close()
                del Connected_Sockets.keys()[Connected_Sockets.values().index(socket)]


if __name__ == "__main__":

    # Inicializa o dicionário de sockets conectados e parâmtros relativos aos sockets     
    Connected_Sockets = {}
    receiving_buffer = 4096
    Port = 5000
     
    # Inicializa o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", Port))
    server_socket.listen(10)
 
    # Adiciona o socket do servidor ao dicionário de
    Connected_Sockets['server'] = server_socket
 
    print "UOL Chat started on Port " + str(Port)
 
    while 1:

        # Busca as listas de sockets disponíveis para leitura, escrita e erro.
        # utiliza os sockets de leitura para leitura das entradas do usuario
        # e também para recebimento de mensagens
        read_sockets,write_sockets,error_sockets = select.select(Connected_Sockets.values(),[],[])
 
        for sock in read_sockets:
            if sock == server_socket:
                # Bloco de código resposável pelo tratamento de uma nova conexão
                # e após estabelecer a conexão envia uma mensagem avisando que o 
                # usuário se conectou a sala
                sockfd, addr = server_socket.accept()
                nickname = sockfd.recv(receiving_buffer)
                Connected_Sockets[nickname] = sockfd
                print "Client " + str(addr) + " connected with nickname " + nickname
                public_message(sockfd, "\r" + nickname + " entered the room!\n")
             
            else:
                try:
                    #Caso a conexão não seja nova realiza os tratamentos para recebimento e envio de mensagens
                    data = sock.recv(receiving_buffer)
                    sender = Connected_Sockets.keys()[Connected_Sockets.values().index(sock)]
                    if '/' not in data :
                        public_message(sock, "\r" + sender + ": " +  data)
                    else:
                        if data == "/list\n":
                            message = "Users in the room:\n"
                            for nickname in Connected_Sockets.keys():
                                if nickname != "server":
                                    message += nickname + "; "
                            private_message(sock, "\r" + message + "\n")
                        elif data == "/quit\n":
                            public_message(sock, "\r" + sender + " has left the room!\n")
                            print "Client " + sender + " " + str(addr) + " disconnected.\n"
                            sock.close()
                            del Connected_Sockets[sender]
                        else:
                            nickname = data.split(" ")
                            nickname = nickname[0].replace("/", "")
                            try:
                                private_message(Connected_Sockets[nickname], "\r\n[PM]" + sender + ": " + data.replace("/" + nickname + " ", "") + "\n")
                            except:
                                private_message(sock, "\rUser not found!\n")
                except:
                    public_message(sock, "Client " + str(addr) + " is offline!")
                    print "Client " + str(addr) + " is offline!" 
                    sock.close()
                    del Connected_Sockets.keys()[Connected_Sockets.values().index(sock)]
                    continue
     
    server_socket.close()
