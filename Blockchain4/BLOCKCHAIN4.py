import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


# === Task 2: SHA-3 vs SHA-256 === #
def task_2_hashing_example():
    data = "Hello, World!"
    sha256_value = hashlib.sha256(data.encode()).hexdigest()
    sha3_hash = hashlib.sha3_256(data.encode()).hexdigest()

    print("Task 2")
    print("Data:", data)
    print("SHA-256 Hash:", sha256_value)
    print("SHA-3 Hash:", sha3_hash)

    # Performance Benchmark
    print("\nPerformance Benchmark:")
    start = time.time()
    for _ in range(100000):
        hashlib.sha256(data.encode()).hexdigest()
    sha256_time = time.time() - start

    start = time.time()
    for _ in range(100000):
        hashlib.sha3_256(data.encode()).hexdigest()
    sha3_time = time.time() - start

    print(f"SHA-256 Time: {sha256_time:.4f}s")
    print(f"SHA-3 Time: {sha3_time:.4f}s")

    """
    Comparison of SHA-3 and SHA-256 Properties:

    1. Algorithm Design:
       - SHA-256: Based on the Merkle-Damgård construction, which is part of the SHA-2 family and has been in use since 2001.
       - SHA-3: Based on a different design called sponge construction, using the Keccak algorithm, introduced in 2015. This design is inherently resistant to length extension attacks.

    2. Security Strength:
       - SHA-256: Offers a security strength of 128 bits (50% probability of collision for 2^128 operations), though it is theoretically vulnerable to length extension attacks if not implemented properly.
       - SHA-3: Provides the same level of collision resistance but does not suffer from the same length extension vulnerabilities due to its sponge-based construction.

    3. Performance:
       - SHA-256: Known for its faster performance in hardware and software implementations and is highly optimized for many use cases.
       - SHA-3: Generally slower than SHA-256 in many common scenarios due to its more complex internal structure, although it is optimized for flexibility and future-proofing.

    4. Versatility:
       - SHA-256: Has a fixed 256-bit output, making it useful for many standard applications (e.g., Bitcoin).
       - SHA-3: Offers a variety of output lengths, from 224 to 512 bits, and also provides extendable output functions (SHAKE128 and SHAKE256), making it more flexible for different use cases.

    5. Adoption and Use Cases:
       - SHA-256: Widely used in blockchain technology (e.g., Bitcoin), digital signatures, and certificate generation.
       - SHA-3: Still relatively new and not as widely adopted as SHA-256, but it is designed to be more future-proof and resilient against new cryptographic threats.
    """


# === Task 3 & 4: Merkle Tree with Verification === #
def calculate_merkle_root(transactions):
    if not transactions:
        return None

    if len(transactions) == 1:
        return transactions[0]

    current_level = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]

    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                combined_hash = hashlib.sha256((current_level[i] + current_level[i + 1]).encode()).hexdigest()
            else:
                combined_hash = hashlib.sha256((current_level[i] + current_level[i]).encode()).hexdigest()
            next_level.append(combined_hash)
        current_level = next_level

    return current_level[0]


def verify_transaction(transactions, target_transaction, expected_merkle_root):
    if target_transaction not in transactions:
        return False

    # Calculate Merkle root after adding the transaction
    calculated_merkle_root = calculate_merkle_root(transactions)
    return calculated_merkle_root == expected_merkle_root


def add_transaction(transactions, new_transaction):
    transactions.append(new_transaction)
    return calculate_merkle_root(transactions)


def remove_transaction(transactions, transaction_to_remove):
    if transaction_to_remove in transactions:
        transactions.remove(transaction_to_remove)
        return calculate_merkle_root(transactions)
    else:
        print(f"Transaction '{transaction_to_remove}' not found.")
        return None


# === Task 5: Secure Message Exchange === #
def generate_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_key(key, is_private=False):
    if is_private:
        return key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
                                 encryption_algorithm=serialization.NoEncryption())
    else:
        return key.public_bytes(encoding=serialization.Encoding.PEM,
                                format=serialization.PublicFormat.SubjectPublicKeyInfo)


def encrypt_message(public_key, message):
    ciphertext = public_key.encrypt(message.encode(),
                                    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                                 label=None))
    return ciphertext


def decrypt_message(private_key, ciphertext):
    decrypted_message = private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                     algorithm=hashes.SHA256(), label=None))
    return decrypted_message.decode()


def task_5_rsa_example():
    print("\nTask 5")

    # Generate key pairs
    alice_private_key, alice_public_key = generate_key_pair()
    bob_private_key, bob_public_key = generate_key_pair()

    # Encrypt & decrypt messages
    message_from_alice = "Hello Bob, this is Alice!"
    encrypted_message_for_bob = encrypt_message(bob_public_key, message_from_alice)
    print("Alice sent an encrypted message to Bob.")

    decrypted_message_by_bob = decrypt_message(bob_private_key, encrypted_message_for_bob)
    print("Bob decrypted the message from Alice:", decrypted_message_by_bob)

    message_from_bob = "Hi Alice, Bob here!"
    encrypted_message_for_alice = encrypt_message(alice_public_key, message_from_bob)
    print("Bob sent an encrypted message to Alice.")

    decrypted_message_by_alice = decrypt_message(alice_private_key, encrypted_message_for_alice)
    print("Alice decrypted the message from Bob:", decrypted_message_by_alice)


# === Task 6: Wallet and Transaction Example === #
def create_wallet():
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                                            encryption_algorithm=serialization.NoEncryption())
    public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                         format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return private_pem, public_pem


def sign_transaction(private_key_pem, transaction):
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(transaction.encode(), ec.ECDSA(hashes.SHA256()))
    return signature


def verify_transaction_signature(public_key_pem, transaction, signature):
    public_key = serialization.load_pem_public_key(public_key_pem)
    try:
        public_key.verify(signature, transaction.encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def add_balance(wallet_balances, public_key_pem, amount):
    if public_key_pem not in wallet_balances:
        wallet_balances[public_key_pem] = 0
    wallet_balances[public_key_pem] += amount


def deduct_balance(wallet_balances, public_key_pem, amount):
    if public_key_pem in wallet_balances and wallet_balances[public_key_pem] >= amount:
        wallet_balances[public_key_pem] -= amount
        return True
    return False


def check_balance(wallet_balances, public_key_pem):
    return wallet_balances.get(public_key_pem, 0)


def task_6_wallet_and_transaction_example():
    print("\nTask 6")

    # Create wallets for Alice and Bob
    alice_private_key, alice_public_key = create_wallet()
    bob_private_key, bob_public_key = create_wallet()

    # Example: Wallet transactions
    wallet_balances = {}
    add_balance(wallet_balances, alice_public_key, 100)
    add_balance(wallet_balances, bob_public_key, 50)

    print("Alice's Balance:", check_balance(wallet_balances, alice_public_key))
    print("Bob's Balance:", check_balance(wallet_balances, bob_public_key))

    # Alice sends $30 to Bob
    transaction = "Alice sends $30 to Bob"
    signature = sign_transaction(alice_private_key, transaction)

    if verify_transaction_signature(alice_public_key, transaction, signature):
        if deduct_balance(wallet_balances, alice_public_key, 30):
            add_balance(wallet_balances, bob_public_key, 30)
            print("Transaction successful!")
        else:
            print("Insufficient funds!")
    else:
        print("Transaction verification failed!")

    print("Alice's Balance after transaction:", check_balance(wallet_balances, alice_public_key))
    print("Bob's Balance after transaction:", check_balance(wallet_balances, bob_public_key))


# Run all tasks
task_2_hashing_example()
task_3_4_merkle_tree_example = lambda: print("\nTask 3 & 4") or print("Initial Merkle Root:",
                                                                      calculate_merkle_root(["T1", "T2"]))
task_3_4_merkle_tree_example()
task_5_rsa_example()
task_6_wallet_and_transaction_example()
