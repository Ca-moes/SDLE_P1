"""
.. module:: node
   :synopsis: Node program that can be a Publisher or a Subscriber
"""
from typing import List

import time
import sys
import zmq
from src.utils import by

def put(socket:zmq.Socket, data:List) -> None:
    """Sends a PUT message

    Args:
        socket (zmq.Socket): Socket to send PUT message through
        data (List): [Topic, Message]
    """
    topic, message = data[0], data[1]
    socket.send(b"PUT\r\n"+by(topic)+b"\r\n"+by(message))
    message = socket.recv()
    print(f"PUT reply: {message}")

def sub(socket:zmq.Socket, data:List) -> None:
    """Sends a SUB message

    Args:
        socket (zmq.Socket): Socket to send SUB message through
        data (List): [Topic]
    """
    topic = data[0]
    socket.send(b"SUB\r\n"+by(topic))
    message = socket.recv()
    print(f'SUB reply: {message}')

def unsub(socket:zmq.Socket, data:List) -> None:
    """Sends a UNSUB message

    Args:
        socket (zmq.Socket): Socket to send UNSUB message through
        data (List): [Topic]
    """
    topic = data[0]
    socket.send(b"UNSUB\r\n"+by(topic))
    message = socket.recv()
    print(f'UNSUB reply: {message}')

def get(socket:zmq.Socket, data:List) -> None:
    """Sends a GET message

    Args:
        socket (zmq.Socket): Socket to send GET message through
        data (List): [Topic]
    """
    topic = data[0]
    socket.send(b"GET\r\n"+by(topic))
    print(f'Sent GET of topic {topic}')
    message = socket.recv()
    print(f"GET reply: {message}")

def main(argv: List):
    """Main function

    Args:
        argv (List): [Node_Identity, (dev)]
    """
    identity = argv[0]
    print(f'Staring node with identity {identity}')
    #  Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt_string(zmq.IDENTITY, identity)
    socket.connect("tcp://localhost:5550")

    if len(argv) > 1 and argv[1] == 'dev':
        try:
            while True:
                command = input("Write a message\nSUB <TOPIC>\nUNSUB <TOPIC>\nGET <TOPIC>\n \
                PUT <TOPIC> <MESSAGE>\n: ")
                command = command.split(' ')
                {
                    'SUB': sub,
                    'UNSUB': unsub,
                    'GET': get,
                    'PUT': put
                }[command[0]](socket, command[1:])
        except KeyboardInterrupt:
            print("Bye")
    else:
        # Test messages as manifests
        if identity == 'SUB1':
            sub(socket, ['TOPIC TOPIC'])
            # To send a PUT
            print("Imma sleep for 5 secs")
            time.sleep(5)
            get(socket, ['TOPIC TOPIC'])
            unsub(socket, ['TOPIC TOPIC'])

        if identity == 'PUB1':
            put(socket, ['TOPIC TOPIC', "Test message"])


if __name__ == "__main__":
    main(sys.argv[1:])
