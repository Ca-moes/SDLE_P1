#
#   Request-reply client in Python
#   Connects REQ socket to tcp://localhost:5559
#   Sends "Hello" to server, expects "World" back
#
import zmq
import time

def main():
    sub_id = -1

    #  Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5550")

    socket.send(b"SUB\r\n"+str(sub_id).encode('utf-8')+b"\r\nTOPIC TOPIC")
    message = socket.recv()
    print(f'SUB reply: {message}')
    sub_id = int(message.decode("utf-8").split('\r\n')[1])

    # To send a PUT
    time.sleep(5)

    socket.send(b"GET\r\n"+str(sub_id).encode('utf-8')+b"\r\nTOPIC TOPIC")
    message = socket.recv()
    print(f'GET reply: {message}')

    socket.send(b"CFM\r\n"+str(sub_id).encode('utf-8')+b"\r\nTOPIC TOPIC")
    message = socket.recv()
    print(f'CFM reply: {message}')

    socket.send(b"UNSUB\r\n"+str(sub_id).encode('utf-8')+b"\r\nTOPIC TOPIC")
    message = socket.recv()
    print(f'UNSUB reply: {message}')

if __name__ == "__main__":
    main()
