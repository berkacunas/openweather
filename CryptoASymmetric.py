import rsa
import logging

def _generateKeys(privatePath, publicPath, size):

	global publicKey, privateKey
	
	# no keys, let's generate them
	logging.info(f'Generating RSA keys of size {size}, please wait...')
	
	publicKey, privateKey = rsa.newkeys(size)
	
	with open(privatePath, 'w') as privKeyFile:
		privKeyFile.write(privateKey.save_pkcs1().decode('UTF-8'))
	
	with open(publicPath, 'w') as pubKeyFile:
		pubKeyFile.write(publicKey.save_pkcs1().decode('UTF-8'))


if __name__ == "__main__":
	
	_generateKeys('prikey', 'pubkey', 512)

	message = "Hello asymmetric crypto! "

	encMessage = rsa.encrypt(message.encode(), 
							publicKey)

	print("original string: ", message)
	print("encrypted string: ", encMessage)

	decMessage = rsa.decrypt(encMessage, privateKey).decode()

	print("decrypted string: ", decMessage)


