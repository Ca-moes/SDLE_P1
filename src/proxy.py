"""
.. module:: proxy
   :synopsis: Proxy program to receive Messages and Send them out
"""
from typing import List
import time
import threading
import pickle
import zmq
from zmq.sugar import socket
from utils import st, by


SAVE_INTERVAL = 5
TO_DELIVER = {} #  { "TOPIC TOPIC": {'SUB1': []} }
MESSAGES =  {} #  { "TOPIC TOPIC": {'counter': 1, 1: "message"} }
WAITING_GET = {} #  { "TOPIC TOPIC": ['SUB1'] }

def print_global_vars(function_name: str) -> None:
    """Prints the internal proxy state

    Args:
        function_name (str): name of calling function
    """
    print(f"""{function_name}:
    - TO_DELIVER: {TO_DELIVER}
    - MESSAGES: {MESSAGES}
    - WAITING_GET: {WAITING_GET}""")

def save_periodic():
    """Function to be run in a separate thread to periodically save the proxy internal state.
    """
    while True:
        # print_global_vars('save_periodic')
        with open('proxy.pickle', 'wb') as file:
            pickle.dump((TO_DELIVER, MESSAGES, WAITING_GET), file)
        time.sleep(SAVE_INTERVAL)

def clean_messages(topic:str, message_counter:int) -> None:
    """Removes messages from MESSAGES if they are not going to be delivered anymore

    Args:
        topic (str): Topic to search for message in
        message_counter (int): Message identifier inside topic
    """
    can_delete_message = True
    for _, to_be_delivered in TO_DELIVER[topic].items():
        if message_counter in to_be_delivered:
            can_delete_message = False
            break
    if can_delete_message:
        MESSAGES[topic].pop(message_counter)

def handle_put(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    """Handler function for PUT message

    Args:
        socket (zmq.Socket): Socket to send response back
        node_id (bytes): Node identifier to send message back
        message (List): Received message
    """
    topic = message[1]
    content = message[2]

    # if topic does not exist, simply drop message
    if TO_DELIVER.get(topic):
        # If topic exists, that topic should exist in MESSAGES (added in SUB)
        MESSAGES[topic]['counter'] += 1

        current_counter = MESSAGES[topic]['counter']
        MESSAGES[topic][current_counter] = content

        # Add message counter to TO_DELIVER
        for subscriber in TO_DELIVER[topic]:
            TO_DELIVER[topic][subscriber].append(current_counter)

    socket.send_multipart([node_id, b'', b'OK'])

    # Send message to Subs blocked in GET
    if WAITING_GET.get(topic):
        for node in WAITING_GET[topic]:
            WAITING_GET[topic].remove(node)
            try:
                socket.send_multipart([by(node), b'', by(content)])
            except Exception as exception:
                print(f'{exception} - Message still queued to send')
            else:
                message_counter = TO_DELIVER[topic][node].pop(0)
                message = MESSAGES[topic][message_counter]
                clean_messages(topic, message_counter)

        if WAITING_GET[topic] == []:
            WAITING_GET.pop(topic)

    print_global_vars('handle_put')

def handle_get(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    """Handler function for GET message

    Args:
        socket (zmq.Socket): Socket to send response back
        node_id (bytes): Node identifier to send message back
        message (List): Received message
    """
    topic = message[1]
    node_id_str = st(node_id)
    # Check if topic exists
    if not TO_DELIVER.get(topic):
        socket.send_multipart([node_id, b'', b"Topic does not exist. Send SUB first"])
        return

    # Check if Subscriber is SUBBED
    if TO_DELIVER[topic].get(node_id_str) is None:
        socket.send_multipart([node_id, b'', b"You are not subbed to this Topic. Send SUB first"])
        return

    # If SUB does not have MESSAGES to send, add to waiting list
    if TO_DELIVER[topic][node_id_str] == []:
        if topic not in WAITING_GET:
            WAITING_GET[topic] = []
        WAITING_GET[topic].append(node_id_str)
        print_global_vars('handle_get - waiting get')
    # If SUB has MESSAGES to send, send them
    else:
        message_counter = TO_DELIVER[topic][node_id_str].pop(0)
        message = MESSAGES[topic][message_counter]
        try:
            socket.send_multipart([node_id, b'', by(message)])
        except zmq.ZMQBaseError:
            print("ZMQ Error - Probably Host Unreachable\nSaving message to send latter")
            TO_DELIVER[topic][node_id_str].append(message_counter)
        else:
            clean_messages(topic, message_counter)
        finally:
            print_global_vars('handle_get - sent message')

def handle_sub(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    """Handler function for sub message

    Args:
        socket (zmq.Socket): Socket to send response back
        node_id (bytes): Node identifier to send message back
        message (List): Received message
    """
    topic = message[1]
    node_id_str = st(node_id)

    # Topic does not exist, create topic to be filled with MESSAGES in PUT
    if not TO_DELIVER.get(topic):
        TO_DELIVER[topic] = {}
        MESSAGES[topic] = {'counter': 0}

    # Not subscribed, create list of MESSAGES to be delivered to sub
    if not TO_DELIVER[topic].get(node_id_str):
        TO_DELIVER[topic][node_id_str] = []
    else:
        print(f'Subscription of NODEID {node_id_str} to topic {topic} already exists')

    print_global_vars('handle_sub')
    socket.send_multipart([node_id, b'', b'OK'])

def handle_unsub(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    """Handler for UNSUB message

    Args:
        socket (zmq.Socket): Socket to send response back
        node_id (bytes): Node identifier to send message back
        message (List): Received message

    Raises:
        Exception: if SUB_ID is not in a topic of TO_DELIVER
    """
    topic = message[1]
    node_id_str = st(node_id)

    if not TO_DELIVER.get(topic):
        print('Subscriber trying to UNSUB non-existing topic')
        socket.send_multipart([node_id, b'', b'ERROR'])

    # these 2 if's need to be done with == None insted of if not because [] == False but [] != None
    if TO_DELIVER[topic].get(node_id_str) is None:
        print('Subscriber trying to UNSUB a topic that it\'s not currently subbed')
        socket.send_multipart([node_id, b'', b'ERROR'])

    if TO_DELIVER[topic].pop(node_id_str, None) is None:
        print(f'TO_DELIVER after pop: {TO_DELIVER}')
        raise Exception("Error in UNSUB - SUB_ID not in topic of TO_DELIVER")

    # Remove topic from MESSAGES and TO_DELIVER if is the last to unsub from that topic
    if len(TO_DELIVER[topic]) == 0:
        #TODO Encapsulate in try..catch or raise Exception if there's an error in pop
        TO_DELIVER.pop(topic)
        MESSAGES.pop(topic)

    print_global_vars('handle_unsub')
    socket.send_multipart([node_id, b'', b'OK'])

def handle_hello(socket:zmq.Socket, node_id:bytes, message: List) -> None:
    """Handler for the Hello message

    Args:
        socket (zmq.Socket): Socket to send response back
        node_id (bytes): Node identifier to send message back
        message (List): Received message (HELLO)
    """
    topics_to_remove = []
    # Verify if node_id is in WAITING_GET and remove it
    for topic, nodes in WAITING_GET.items():
        if st(node_id) in nodes:
            WAITING_GET[topic].remove(st(node_id))
            topics_to_remove.append(topic)
    for topic in topics_to_remove:
        if WAITING_GET[topic] == []:
            WAITING_GET.pop(topic)

    print_global_vars('handle_hello')
    socket.send_multipart([node_id, b'', b'HI'])


def process_msg(socket:zmq.Socket, message:List) -> None:
    """Receives a message and sends it to the proper handler

    Args:
        socket (zmq.Socket): Socket to send response back
        message (List): Message received
    """
    node_id = message[0]
    message = message[2].decode("utf-8").split('\r\n')

    {   'PUT': handle_put,
        'GET': handle_get,
        'SUB': handle_sub,
        'UNSUB': handle_unsub,
        'HELLO': handle_hello
    }[message[0]](socket, node_id, message)

def main() -> None:
    """Main function
    """
    global TO_DELIVER, MESSAGES, WAITING_GET
    try:
        with open('proxy.pickle', 'rb') as file:
            print("Loading Proxy State")
            TO_DELIVER, MESSAGES, WAITING_GET = pickle.load(file)
    except FileNotFoundError:
        print("Didn't find a Proxy State, starting anew")

    # Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.setsockopt(zmq.ROUTER_MANDATORY, 1)
    socket.bind("tcp://*:5550")

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    # Thread to save state
    save_thread = threading.Thread(target=save_periodic)
    save_thread.daemon = True
    save_thread.start()

    # Poll MESSAGES
    try:
        while True:
            socks = dict(poller.poll())

            if socks.get(socket) == zmq.POLLIN:
                message = socket.recv_multipart()
                process_msg(socket, message)
    except KeyboardInterrupt:
        print(" W: interrupt received...")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
