from typing import List
import zmq
import time

from zmq.error import ZMQError

# to_deliver = { "TOPIC TOPIC": {'SUB1': []}}
to_deliver = {}
to_confirm = {}
messages = {}
last_sub_id = 0

def print_global_vars(function_name: str):
    print(f'{function_name}:\n- to_deliver: {to_deliver}\n- to_confirm: {to_confirm}\n- messages: {messages}')

def handle_put(message:List) -> bytes:
    """Handler for the PUT message.
    If the topic does not exist, it means there are no subs, so the message is dropped

    Args:
        message (List): [PUT, Topic, Content]

    Returns:
        bytes: "OK" message
    """
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

def handle_sub(message: List) -> bytes:
    """Handler for the SUB message.
    If the topic does not exist, it creates the topic in to_deliver and messages

    Args:
        message (List): [SUB, SUB_ID, TOPIC]

    Raises:
        Exception: When A SUB message arrives with SUB_ID larger than local count

    Returns:
        bytes: Response to send back
    """
    sub_id = int(message[1])
    topic = message[2]

    if (sub_id == -1):
        global last_sub_id  # https://docs.python.org/3/reference/executionmodel.html#naming-and-binding
        last_sub_id += 1
        sub_id = last_sub_id
    elif (sub_id > last_sub_id):
        raise Exception("Careful, subscriber using ID not given by Proxy")

    # Topic does not exist, create topic to be filled with messages in PUT
    if not (to_deliver.get(topic)):
        to_deliver[topic] = {}
        to_confirm[topic] = {}
        messages[topic] = {'counter': 0}

    # Not subscribed, create list of messages to be deliveed to sub
    if not (to_deliver[topic].get(sub_id)):
        to_deliver[topic][sub_id] = []
        to_confirm[topic][sub_id] = []
    else:
        print(f'Subscription of SUBID {sub_id} to topic {topic} already exists')

    print_global_vars('handle_sub')
    return b"OK\r\n" + str(sub_id).encode('utf-8')

def handle_unsub(message: List) -> bytes:
    """Handler for the Unsubscription

    Args:
        message (List): ["UNSUB", Subscriber ID, Topic]

    Raises:
        Exception: If there's an error while altering the dict

    Returns:
        bytes: return message : "OK"
    """

    sub_id = int(message[1])
    topic = message[2]

    if not (to_deliver.get(topic)):
        print(f'TO IMPLEMENT: Subscriber trying to UNSUB non-existing topic')
        return b"OK"

    if not (to_deliver[topic].get(sub_id)):
        print(f'TO IMPLEMENT: Subscriber trying to UNSUB a topic that it\'s not currently subbed')
        return b"OK"

    if not (to_deliver[topic].pop(sub_id, None)):
        raise Exception("Error in UNSUB - SUB_ID not in topic of to_deliver")

    # Remove topic from messages and to_deliver if is the last to unsub from that topic
    # Don't remove in to_confirm, could have not confirmed messages in there
    if(len(to_deliver[topic]) == 0):
        # TODO Encapsulate in try..catch or raise Exception if there's an error in pop
        to_deliver.pop(topic)
        messages.pop(topic)

    print_global_vars('handle_sub')
    return b"OK"

def handle_cfm(message: List) -> bytes:
    """message: ["CFM", Subscriber ID, Message ID] """
    sub_id = int(message[1])
    topic = message[2]


    print_global_vars('handle_cfm')
    return b"Not Implemented"

def process_msg(ret_address, message: List) -> List:
    message_type = message[0]

    new_message = {
        'PUT': handle_put,
        'GET': handle_get,
        'SUB': handle_sub,
        'UNSUB': handle_unsub,
        'CFM': handle_cfm
    }[message_type](message)

    return [ret_address, b'', new_message]

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

                response = process_msg(message[0], message[2].decode("utf-8").split('\r\n'))

                return_value = socket.send_multipart(response)
                print(f'proxy send_multipart return: {return_value}')
    except KeyboardInterrupt:
        print("W: interrupt received, stopping...")
    except Exception as e:
        print(f" {e}: error [interrupt received, stopping...]")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
