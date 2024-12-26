from ecdsa import SigningKey, VerifyingKey
# Generate a key pair
private_key = SigningKey.generate()
public_key = private_key.get_verifying_key()
# Sign a message
message = "Blockchain is secure."
signature = private_key.sign(message.encode())
# Verify the signature
if public_key.verify(signature, message.encode()):
    print("Signature is valid.")
else:
    print("Signature is invalid.")