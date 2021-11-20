#
#   Request-reply client in Python
#   Connects REQ socket to tcp://localhost:5559
#   Sends "Hello" to server, expects "World" back
#
import zmq, time, sys
from utils import by

def put(socket:zmq.Socket, topic:str, message:str) -> None:
    socket.send(b"PUT\r\n"+by(topic)+b"\r\n"+by(message))
    message = socket.recv()
    print(f"PUT reply: {message}")

def sub(socket:zmq.Socket, topic:str) -> None:
    socket.send(b"SUB\r\n"+by(topic))
    message = socket.recv()
    print(f'SUB reply: {message}')

def unsub(socket:zmq.Socket, topic:str) -> None:
    socket.send(b"UNSUB\r\n"+by(topic))
    message = socket.recv()
    print(f'UNSUB reply: {message}')

def get(socket:zmq.Socket, topic:str) -> None:
    socket.send(b"GET\r\n"+by(topic))
    print(f'Sent GET of topic {topic}')
    message = socket.recv()
    print(f"PUT reply: {message}")

def main(argv):
    identity = argv[0]
    #  Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt_string(zmq.IDENTITY, identity)
    socket.connect("tcp://localhost:5550")


    if identity == 'SUB1':
        # Send/Receive messages
        sub(socket, 'TOPIC TOPIC')

        # To send a PUT
        # print("Imma sleep for 5 secs")
        # time.sleep(5)

        get(socket, 'TOPIC TOPIC')
        unsub(socket, 'TOPIC TOPIC')

    if identity == 'PUB1':
        put(socket, 'TOPIC TOPIC', "Test message")


if __name__ == "__main__":
    main(sys.argv[1:])
