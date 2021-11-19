from typing import List
import zmq

# to_deliver = { "TOPIC TOPIC": {'SUB1': []}}
to_deliver = {}
to_confirm = {}
messages = {}
last_sub_id = -1

def handle_put(message:List) -> bytes:
    """Handler for the PUT message

    Args:
        message (List): [PUT, Topic, Content]

    Returns:
        bytes: "OK" message
    """
    topic = message[1]
    content = message[2]

    if(to_deliver.get(topic) != None):
        #Add message to messages list
        if(messages.get(topic) != None):
            #increment counter
            messages[topic]['counter'] += 1
        else:
            #set initial counter
            messages[topic] = {}
            messages[topic]['counter'] = 0

        current_counter = messages[topic]['counter']
        messages[topic][current_counter] = content

        #Add message to deliver
        for subscriber in to_deliver[topic]:
            to_deliver[topic][subscriber].append(content)

    print(f'handle_put: {messages}')
    return b"OK"

def handle_get(message: List):
    """message: [return address, "GET", [Subscriber ID, Topic]]"""

    # Mexe em estado interno
    # Cria mensagem
    # Retorna
    return [message[0], b'', b"Not Implemented"]

def handle_sub(message: List) -> bytes:
    """Handler for the SUB message

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

    if(to_deliver.get(topic) == None):
        to_deliver[topic] = {}

    if(to_deliver[topic].get(sub_id) == None):
        to_deliver[topic][sub_id] = []
    else:
        print(f'Subscription of SUBID {sub_id} to topic {topic} already exists')

    print(f'to_deliver in sub = {to_deliver}')
    return b"OK\r\n" + str(sub_id).encode('utf-8')

def handle_unsub(message: List):
    """message: ["UNSUB", Subscriber ID, Topic] """
    sub_id = int(message[1])
    topic = message[2]

    if(to_deliver.get(topic) == None):
        print(f'TO IMPLEMENT: Subscriber trying to UNSUB non-existing topic')
        return b"OK"

    if(to_deliver[topic].get(sub_id) == None):
        print(f'TO IMPLEMENT: Subscriber trying to UNSUB a topic that it\'s not currently subbed')
        return b"OK"

    if(to_deliver[topic].pop(sub_id, None) == None):
        raise Exception("Error in UNSUB")

    print(f'to_deliver in unsub = {to_deliver}')
    return b"OK"

def handle_cfm(message: List):
    """message: ["CFM", Subscriber ID, Message ID] """

    # Mexe em estado interno
    # Cria mensagem
    # Retorna
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

                socket.send_multipart(response)
    except KeyboardInterrupt:
        print(" W: interrupt received, stopping...")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
