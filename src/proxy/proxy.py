# Simple request-reply broker
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import zmq

def main():
    # Prepare our context and sockets
    context = zmq.Context()
    pub_socket = context.socket(zmq.ROUTER)
    sub_socket = context.socket(zmq.ROUTER)
    pub_socket.bind("tcp://*:5551")
    sub_socket.bind("tcp://*:5550")

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(pub_socket, zmq.POLLIN)
    poller.register(sub_socket, zmq.POLLIN)

    # Switch messages between sockets
    while True:
        socks = dict(poller.poll())

        if socks.get(pub_socket) == zmq.POLLIN:
            message = pub_socket.recv_multipart()
            pub_socket.send_multipart(message)

        if socks.get(sub_socket) == zmq.POLLIN:
            message = sub_socket.recv_multipart()
            sub_socket.send_multipart(message)


if __name__ == "__main__":
    main()
