###########################################################################
# Concurrent server - webserver3d.py                                      #
#                                                                         #
# Tested with Python 2.7.9 & Python 3.4 on Ubuntu 14.04 & Mac OS X        #
#                                                                         #
# - Parent and child processes DO NOT close duplicate descriptors         #
# - Client connections are not terminated                                 #
# - Server might run out of descriptors                                   #
#   * Set a limit of open files to 256 ($ ulimit -n 256)                  #
#   * Use $ python client3.py to simulate the behavior                    #
# - OMG, Zombies!!! Server might run out of processes                     #
#   * $ curl and $ ps to see zombies                                      #
#   * Set max user processes to 400 ($ ulimit -u 400)                     #
#   * Use $ python client3.py to simulate the behavior                    #
#                                                                         #
###########################################################################
import os
import socket

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def handle_request(client_connection):
    request = client_connection.recv(1024)
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    clients = []
    while True:
        client_connection, client_address = listen_socket.accept()
        # store the reference otherwise it's garbage collected
        # on the next loop run
        clients.append(client_connection)
        pid = os.fork()
        if pid == 0:  # child
            listen_socket.close()  # close child copy
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)  # child exits here
        else:  # parent
            # client_connection.close()
            print(len(clients))

if __name__ == '__main__':
    serve_forever()


# try: curl http://localhost:8888/hello
# and server did not terminate and kept hanging > 
# why?:  The server no longer sleeps for 60 seconds: its child process actively handles a client request, closes the client connection and exits, but the client curl still does not terminate.

# why does the curl not terminate? 
# The reason is the duplicate file descriptors. When the child process closed the client connection, the kernel decremented the reference count of that client socket and the count became 1. 
# The server child process exited, but the client socket was not closed by the kernel because the reference count for that socket descriptor was not 0
# Then, the termination packet (called FIN in TCP/IP parlance) was not sent to the client and the client stayed on the line
# If your long-running server doesn’t close duplicate file descriptors, it will eventually run out of available file descriptors



#takeaways:
# 1.If you don’t close duplicate descriptors, the clients won’t terminate because the client connections won’t get closed.
# 2.If you don’t close duplicate descriptors, your long-running server will eventually run out of available file descriptors (max open files).
# 3.When you fork a child process and it exits and the parent process doesn’t wait for it and doesn’t collect its termination status, it becomes a zombie.
# 4.Zombies need to eat something and, in our case, it’s memory. Your server will eventually run out of available processes (max user processes) if it doesn’t take care of zombies.
# 5.You can’t kill a zombie, you need to wait for it.
