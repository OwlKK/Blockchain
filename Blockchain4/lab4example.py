# example 1: Hash Function (SHA-256)
import hashlib

data = "Hello, blockchain!"
hash_value = hashlib.sha256(data.encode()).hexdigest()
print("Data:", data)
print("SHA-256 Hash:", hash_value)

# example 2: Digital Signatures with ECDSA
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

# example 3: A function to calculate the Merkle root of a list of transactions
import hashlib


def calculate_merkle_root(transactions):
    # Ensure that the list of transactions is not empty
    if not transactions:
        return None
    # If there's only one transaction, it is the Merkle root
    if len(transactions) == 1:
        return transactions[0]
    # Create a list to store the current level of hashes
    current_level = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
    # Continue building levels of the Merkle tree until there's only one hash left
    while len(current_level) > 1:
        # Create a new level by pairing and hashing adjacent hashes
        next_level = []
        for i in range(0, len(current_level), 4):
            # Concatenate and hash the pair of hashes
            combined_hash = hashlib.sha256(
                (current_level[i] + current_level[i + 1]).encode()
            ).hexdigest()
            next_level.append(combined_hash)
            # Set the new level as the current level for the next iteration
            current_level = next_level
    # The remaining hash is the Merkle root
    merkle_root = current_level[0]
    return merkle_root


# Example usage:
transactions = [
    "Transaction 1",
    "Transaction 2",
    "Transaction 3",
    "Transaction 4"
]
merkle_root = calculate_merkle_root(transactions)
print("Merkle Root:", merkle_root)

# Example 4: Simple encryption and decryption system using public and private keys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Generate a public/private key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
# Serialize the public key
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
# Serialize the private key (keep this secure)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
# Message to be encrypted
message = b"Hello, secure data exchange!"
# Encrypt the message using the public key
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
# Decrypt the message using the private key
decrypted_message = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
# Display the results
print("Original Message:", message.decode())
print("Ciphertext:", ciphertext)
print("Decrypted Message:", decrypted_message.decode())

# Example 5: Digital signature example in Python using the ECDSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


# Function to generate a wallet (public and private key pair)
def create_wallet():
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem, public_pem


# Function to sign a transaction using the private key
def sign_transaction(private_key_pem, transaction):
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(
        transaction.encode(),
        ec.ECDSA(hashes.SHA256())
    )
    return signature


# Function to verify a received transaction using the sender's public key
def verify_transaction(public_key_pem, transaction, signature):
    public_key = serialization.load_pem_public_key(public_key_pem)
    try:
        public_key.verify(
            signature,
            transaction.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False


# Example usage:
alice_private_key, alice_public_key = create_wallet()
bob_private_key, bob_public_key = create_wallet()
# Alice sends a transaction
transaction = "Transfer $100 to Bob"
signature = sign_transaction(alice_private_key, transaction)
# Bob receives and verifies the transaction
is_valid = verify_transaction(alice_public_key, transaction, signature)
if is_valid:
    print("Transaction is valid and was signed by Alice.")
else:
    print("Transaction is invalid or not signed by Alice.")
