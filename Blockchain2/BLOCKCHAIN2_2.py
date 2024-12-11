import hashlib


def proof_of_work(block, target):
    nonce = 0
    while True:
        data = f'{block}{nonce}'.encode()
        hash_result = hashlib.sha256(data).hexdigest()
        if hash_result[:len(target)] == target:
            return nonce
        nonce += 1


block_data = "Transaction data"
target_prefix = "0000"
nonce = proof_of_work(block_data, target_prefix)
print(f"Valid nonce found: {nonce}")
