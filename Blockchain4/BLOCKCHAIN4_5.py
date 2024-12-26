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
