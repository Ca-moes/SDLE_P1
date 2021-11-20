from typing import List
import zmq, time

from zmq.sugar import context
from utils import st, by

to_deliver = {}  # { "TOPIC TOPIC": {'SUB1': []} }
messages = {}  # { "TOPIC TOPIC": {counter: 1, 1: "message"} }
waiting_get = {} # { "TOPIC TOPIC": [SUB1] }

def print_global_vars(function_name: str):
    print(f"""{function_name}:
    - to_deliver: {to_deliver}
    - messages: {messages}
    - waiting_get: {waiting_get}""")

def handle_put(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    topic = message[1]
    content = message[2]

    # if topic does not exist, simply drop message
    if(to_deliver.get(topic)):
        # If topic exists, that topic should exist in messages (added in SUB)
        messages[topic]['counter'] += 1

        current_counter = messages[topic]['counter']
        messages[topic][current_counter] = content

        # Add message counter to to_deliver
        for subscriber in to_deliver[topic]:
            to_deliver[topic][subscriber].append(current_counter)

    print_global_vars('handle_put')
    socket.send_multipart([node_id, b'', b'OK'])

    # Send message to Subs blocked in GET
    if (waiting_get.get(topic)):
        for node_id in waiting_get[topic]:
            socket.send_multipart([by(node_id), b'', by(content)])

def handle_get(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    topic = message[1]
    node_id_str = st(node_id)
    # Check if topic exists
    if not (to_deliver.get(topic)):
        print(f'TO IMPLEMENT: Subscriber trying to GET from a non-existing topic')
        return b"TO BE IMPLEMENTED - NON EXISTENT TOPIC"

    # Check if Subscriber is SUBBED
    if(to_deliver[topic].get(node_id_str) == None):
        print(f'TO IMPLEMENT: Subscriber trying to GET from a topic to which it is not SUBBED')
        return b"TO BE IMPLEMENTED - NOT SUBBED"

    # If SUB does not have messages to send, add to waiting list
    if (to_deliver[topic][node_id_str] == []):
        if topic not in waiting_get:
            waiting_get[topic] = []
        waiting_get[topic].append(node_id_str)
    # If SUB has messages to send, send them
    else:
        message_counter = to_deliver[topic][node_id_str].pop(0)
        message = messages[topic][message_counter]

        print_global_vars('handle_get')
        socket.send_multipart([node_id, b'', by(message)])

def handle_sub(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    topic = message[1]
    node_id_str = st(node_id)

    # Topic does not exist, create topic to be filled with messages in PUT
    if not (to_deliver.get(topic)):
        to_deliver[topic] = {}
        messages[topic] = {'counter': 0}

    # Not subscribed, create list of messages to be delivered to sub
    if not (to_deliver[topic].get(node_id_str)):
        to_deliver[topic][node_id_str] = []
    else:
        print(f'Subscription of NODEID {node_id_str} to topic {topic} already exists')

    print_global_vars('handle_sub')
    socket.send_multipart([node_id, b'', b'OK'])

def handle_unsub(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    topic = message[1]
    node_id_str = st(node_id)

    if not (to_deliver.get(topic)):
        print(f'TO IMPLEMENT: Subscriber trying to UNSUB non-existing topic')
        socket.send_multipart([node_id, b'', b'ERROR'])

    # these 2 if's need to be done with == None insted of if not because [] == False but [] != None
    if (to_deliver[topic].get(node_id_str) == None):
        print(f'TO IMPLEMENT: Subscriber trying to UNSUB a topic that it\'s not currently subbed')
        socket.send_multipart([node_id, b'', b'ERROR'])

    if (to_deliver[topic].pop(node_id_str, None) == None):
        print(f'to_deliver after pop: {to_deliver}')
        raise Exception("Error in UNSUB - SUB_ID not in topic of to_deliver")

    # Remove topic from messages and to_deliver if is the last to unsub from that topic
    if(len(to_deliver[topic]) == 0):
        # TODO Encapsulate in try..catch or raise Exception if there's an error in pop
        to_deliver.pop(topic)
        messages.pop(topic)

    print_global_vars('handle_sub')
    socket.send_multipart([node_id, b'', b'OK'])

def process_msg(socket:zmq.Socket, message:List) -> None:
    node_id = message[0]
    message = message[2].decode("utf-8").split('\r\n')

    {   'PUT': handle_put,
        'GET': handle_get,
        'SUB': handle_sub,
        'UNSUB': handle_unsub,
    }[message[0]](socket, node_id, message)


def main():
    # Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.setsockopt(zmq.ROUTER_MANDATORY, 1)
    socket.bind("tcp://*:5550")

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    try:
        # Switch messages between sockets
        while True:
            socks = dict(poller.poll())

            if socks.get(socket) == zmq.POLLIN:
                message = socket.recv_multipart()  # https://zguide.zeromq.org/docs/chapter3/#The-Simple-Reply-Envelope
                process_msg(socket, message)
    except KeyboardInterrupt:
        print("W: interrupt received, stopping...")
    except Exception as e:
        print(f"{e}")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
