from typing import List
import zmq, os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

to_deliver = { "TOPIC TOPIC": {'SUB1': []}
             }
to_confirm = {}
messages = {}
last_sub_id = -1

def handle_put(message:List):
    """message: [return address, "PUT", [Topic, Content]]"""
    topic = message[2][0]
    content = message[2][1]

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
            # subscriber.append(content)

    print(f'handle_put: {messages}')
    return [message[0], b'', b"OK"]

def handle_get(message: List):
    """message: [return address, "GET", [Subscriber ID, Topic]]"""

    # Mexe em estado interno
    # Cria mensagem
    # Retorna
    pass

def handle_sub(message: List):
    """message: [return address, "SUB", [Subscriber ID, Topic]]"""
    sub_id = message[2][0]
    topic = message[2][1]

    if (sub_id == -1):
        pass
    # Mexe em estado interno
    # Cria mensagem
    # Retorna
    pass

def handle_unsub(message: List):
    """message: [return address, "UNSUB", [Subscriber ID, Topic]]"""

    # Mexe em estado interno
    # Cria mensagem
    # Retorna
    pass

def handle_cfm(message: List):
    """message: [return address, "CFM", [Subscriber ID, Message ID]]"""

    # Mexe em estado interno
    # Cria mensagem
    # Retorna
    pass

def process_msg(message: List) -> List:
    """ Returns: [return address, message type, message elements] """
    message_type = message[1]

    if(message_type=="PUT"):
        return handle_put(message)
    elif(message_type=="GET"):
        return handle_get(message)
    elif(message_type=="SUB"):
        return handle_sub(message)
    elif(message_type=="UNSUB"):
        return handle_unsub(message)
    elif(message_type=="CFM"):
        return handle_cfm(message)

    return ""

def main():
    # Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind("tcp://*:5550")

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    # Switch messages between sockets
    while True:
        socks = dict(poller.poll())

        if socks.get(socket) == zmq.POLLIN:
            message = socket.recv_multipart()  # https://zguide.zeromq.org/docs/chapter3/#The-Simple-Reply-Envelope

            print(f'1: {message[0]}\n2: {message[1]}\n3: {message[2]}')
            new_message = [message[0], b'', b'New Message']

            parsed_msg = utils.parse_message(message)
            new_message = process_msg(parsed_msg)

            socket.send_multipart(new_message)



if __name__ == "__main__":
    main()