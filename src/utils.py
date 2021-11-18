from typing import List

def parse_message_proxy(message: List) -> List:
    """ Returns: [Return Address, Message Type, Array of message elements] """
    return_address = message[0]
    message = message[2].decode("utf-8")
    message = message.split('\r\n')

    return [return_address, message[0], message[1:]]

# def parse_message(message: bytes):
#     message = message.decode("utf-8").split('\r\n')

