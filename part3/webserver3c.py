###########################################################################
# Concurrent server - webserver3c.py                                      #
#                                                                         #
# Tested with Python 2.7.9 & Python 3.4 on Ubuntu 14.04 & Mac OS X        #
#  
# - handle multiple client requests at the same time (fork())                                                                  #
# - Child process sleeps for 15 seconds after handling a client's request #
# - Parent and child processes close duplicate descriptors                #
#                                                                         #
###########################################################################
import os
import socket
import time

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(
        'Child PID: {pid}. Parent PID {ppid}'.format(
            pid=os.getpid(),
            ppid=os.getppid(),
        )
    )
    print(request.decode())
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    time.sleep(5)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))
    print('Parent PID (PPID): {pid}\n'.format(pid=os.getpid()))

    while True:
        client_connection, client_address = listen_socket.accept()
        pid = os.fork()
        if pid == 0:  # child
            listen_socket.close()  # close child copy
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)  # child exits here
        else:  # parent
            client_connection.close()  # close parent copy and loop over

if __name__ == '__main__':
    serve_forever()

    
# 1.The simplest way to write a concurrent server in Unix is to use the fork() system call
# 2.When a process forks a new process it becomes a parent process to that newly forked child process.
# 3.Parent and child share the same file descriptors after the call to fork.
# 4.The kernel uses descriptor reference counts to decide whether to close the file/socket or not
# 5.The role of a server parent process: all it does now is accept a new connection from a client, fork a child to handle the client request, and loop over to accept a new client connection.
