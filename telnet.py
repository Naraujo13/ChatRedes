import socket, select, string, sys
 
def prompt() :
    sys.stdout.flush()
    sys.stdout.write('<You> ')
    sys.stdout.flush()

 
if __name__ == "__main__":
     
    if(len(sys.argv) < 4) :
        print 'Usage : python telnet.py hostname port'
        sys.exit()
     
    host = sys.argv[1]
    port = int(sys.argv[2])
    nickname = sys.argv[3]
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # Realiza a tentativa de conexão a um host
    try :
        s.connect((host, port))
        s.send(nickname)
        prompt()
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'You connected to the UOL Chat!. Have fun!'
    prompt()
     
    while 1:
        socket_list = [sys.stdin, s]

        # Como no servidor, busca a lista de sockets prontos para leitura
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            # Verifica os sockets que possuem mensagem e trata o recebimento da mensagem
            # imprimindo a mesma na tela do usuário
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from UOL Chat!'
                    sys.exit()
                else :
                    sys.stdout.write(data)
                    prompt()

            # Caso o socket lido tenha sido o própio, le a mensagem do console e envia
            else :
                msg = sys.stdin.readline()
                s.send(msg)
                prompt()
