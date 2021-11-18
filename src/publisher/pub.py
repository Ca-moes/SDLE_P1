#
#   Request-reply client in Python
#   Connects REQ socket to tcp://localhost:5559
#   Sends "Hello" to server, expects "World" back
#
import zmq
from zmq.backend import Frame

def main():
    #  Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5550")

    #  Do 10 requests, waiting each time for a response
    for request in range(1, 10):
        socket.send(b"PUT\r\nTOPIC TOPIC\r\nMESSAGE")
        message = socket.recv()
        print(f"Received reply {request} [{message}]")

if __name__ == "__main__":
    main()