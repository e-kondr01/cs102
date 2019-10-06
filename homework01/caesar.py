def encrypt_caesar(plaintext: str) -> str:
    """
    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    shift = 3
    ciphertext = ''
    for char in plaintext:
        if (ord(char) > 64 and ord(char) < 91 - shift or
                ord(char) > 96 and ord(char) < 123 - shift):
            ciphertext += chr(ord(char) + shift)
        elif (ord(char) > 90 - shift and ord(char) < 91 or
                ord(char) > 122 - shift and ord(char) < 123):
            ciphertext += chr(ord(char) - 26 + shift)
        else:
            ciphertext += char
    return ciphertext


def decrypt_caesar(ciphertext: str) -> str:
    """
    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    shift = 3
    plaintext = ''
    for char in ciphertext:
        if (ord(char) > 64 + shift and ord(char) < 91 or
                ord(char) > 96 + shift and ord(char) < 123):
            plaintext += chr(ord(char) - shift)
        elif (ord(char) > 64 and ord(char) < 65 + shift or
                ord(char) > 96 and ord(char) < 97 + shift):
            plaintext += chr(ord(char) + 26 - shift)
        else:
            plaintext += char
    return plaintext
