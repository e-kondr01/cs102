def encrypt_vigenere(plaintext, keyword):
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ''
    i = 0
    KeywordLength = len(keyword)
    for char in plaintext:
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            shift = ord(keyword.lower()[i]) - 97
            if ord(char) + shift > ord('z'):
                ciphertext += chr(ord(char) + shift - 26)
            elif ('A' <= char <= 'Z' and
                    ord(char) + shift > ord('Z')):
                ciphertext += chr(ord(char) + shift - 26)
            else:
                ciphertext += chr(ord(char) + shift)
            i += 1
            if i == KeywordLength:
                i = 0
        else:
            ciphertext += char
    return ciphertext


def decrypt_vigenere(ciphertext, keyword):
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ''
    i = 0
    KeywordLength = len(keyword)
    for char in ciphertext:
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            shift = 97 - ord(keyword.lower()[i])
            if ord(char) + shift < ord('A'):
                plaintext += chr(ord(char) + shift + 26)
            elif ('a' <= char <= 'z' and
                    ord(char) + shift < ord('a')):
                plaintext += chr(ord(char) + shift + 26)
            else:
                plaintext += chr(ord(char) + shift)
            i += 1
            if i == KeywordLength:
                i = 0
        else:
            plaintext += char
    return plaintext
