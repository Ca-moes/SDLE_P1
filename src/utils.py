"""
.. module:: utils
   :synopsis: Utility functions used by Node and Proxy
"""
def by(message:str) -> bytes:
    """Converts a string to bytes

    Args:
        message (str): string to be converted

    Returns:
        bytes: bytes representation of the string
    """
    return message.encode('utf-8')

def st(message:bytes) -> str:
    """Converts a bytes message to string

    Args:
        message (bytes): bytes message to be converted

    Returns:
        str: String representation of the bytes message
    """
    return message.decode('utf-8')
