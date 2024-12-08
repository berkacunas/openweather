from cryptography.fernet import Fernet

def generate_key():

    return Fernet.generate_key()

def encrypt_message(message, key) -> str:

    if not isinstance(message, str):
        message = str(message)
        
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message

def decrypt_message(encrypted_message, key) -> str:
    
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()

if __name__ == "__main__":
    
    key = generate_key()
    encrypted_message = encrypt_message("Hello Cryptography !", key)
    print(encrypted_message)

    decrypted_message = decrypt_message(encrypted_message, key)
    print(decrypted_message)
    