from cryptography.fernet import Fernet

def generate_key():

    key = Fernet.generate_key()
    with open("data/secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():

    return open("data/secret.key", "rb").read()

def encrypt_message(message):

    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    print(encrypted_message)

def decrypt_message(encrypted_message):
    
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    print(decrypted_message.decode())

if __name__ == "__main__":
    
    #generate_key()
    encrypt_message("Hello Cryptography !")
    decrypt_message(b'gAAAAABnOkctUVhYSiQ-2lbGOepYva5lA5PWN0zogfIQCQCMfghuvYDpzT983vEbJKVdeAWyhDwlhnzWlmTYtfgZGvT8QnIqXCLxiaFX69n6VGC0hEVQOuc=')
