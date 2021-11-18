from typing import List

def parse_message(message: List) -> List:
    """ Returns: [Endereço de retorno, NULL, Mensagem] """
    return_address = message[0]
    message = message[2].decode("utf-8")
    print(f'message: {message}')
    message = message.split('\r\n')
    message_type = message[0]

    message_parsed = [return_address, message_type, message[1:]]
    return message_parsed
