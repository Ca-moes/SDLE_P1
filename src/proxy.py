from typing import List
import zmq, time
from utils import st

# to_deliver = { "TOPIC TOPIC": {'SUB1': []}}
to_deliver = {}
messages = {}
waiting_get = []

def print_global_vars(function_name: str):
    print(f'{function_name}:\n- to_deliver: {to_deliver}\n- messages: {messages}')

def handle_put(message:List) -> bytes:
    # TODO ver se a mensagem tup que recebeu tem de ser mandada como resposta a algum get
    topic = message[1]
    content = message[2]

    if(to_deliver.get(topic)):
        #Add message to messages list
        if(messages.get(topic)):
            #increment counter
            messages[topic]['counter'] += 1
        else:
            #set initial counter
            messages[topic] = {}
            messages[topic]['counter'] = 0

        current_counter = messages[topic]['counter']
        messages[topic][current_counter] = content

        #Add message counter to to_deliver
        for subscriber in to_deliver[topic]:
            to_deliver[topic][subscriber].append(current_counter)

    print_global_vars('handle_put')
    return b"OK"

def handle_get(message: List) -> bytes:
    """Handler for the GET message

    Args:
        message (List): ["GET", Subscriber ID, Topic]

    Returns:
        bytes: return message
    """
    print("IN GET HANDLER")
    sub_id = int(message[1])
    topic = message[2]

    # Check if topic exists
    if(to_deliver.get(topic) == None):
        print(f'TO IMPLEMENT: Subscriber trying to GET from a non-existing topic')
        return b"TO BE IMPLEMENTED - NON EXISTENT TOPIC"

    # Check if Subscriber is SUBBED
    if(to_deliver[topic].get(sub_id) == None):
        print(f'TO IMPLEMENT: Subscriber trying to GET from a topic to which it is not SUBBED')
        return b"TO BE IMPLEMENTED - NOT SUBBED"

    # Check if SUB has messages in Topic
    if not (to_deliver[topic][sub_id]):
        print(f'TO IMPLEMENT: Subscriber trying to GET from a SUBBED Topic without messages')
        return b"TO BE IMPLEMENTED - BLOCK IF NO MESSAGES"

    message_counter = to_deliver[topic][sub_id].pop(0)
    message = messages[topic][message_counter]

    print("sleeping to let sub crash")
    time.sleep(5)

    print_global_vars('handle_get')
    return b"MSG\r\n" + str(message_counter).encode('utf-8') + b"\r\n"+ message.encode('utf-8')

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
