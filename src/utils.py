def by(message:str) -> bytes:
    return message.encode('utf-8')

def st(message:bytes) -> str:
    return message.decode('utf-8')
