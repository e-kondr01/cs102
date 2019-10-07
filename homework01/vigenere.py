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
        if (ord(char) + ord(keyword.lower()[i]) - 97 > 122 or
                char.lower() != char and
                ord(char) + ord(keyword.lower()[i]) - 97 > 92):
            ciphertext +=  chr(ord(char) + ord(keyword.lower()[i]) - 97 - 26)
        else:
            ciphertext += chr(ord(char) + ord(keyword.lower()[i]) - 97)
        i += 1
        if i == KeywordLength:
            i = 0
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
    # PUT YOUR CODE HERE
    return plaintext
print(encrypt_vigenere(input(), input()))