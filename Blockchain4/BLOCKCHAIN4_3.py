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
        for i in range(0, len(current_level), 2):
            # If there's an odd number of hashes, duplicate the last one
            if i + 1 < len(current_level):
                # Concatenate and hash the pair of hashes
                combined_hash = hashlib.sha256(
                    (current_level[i] + current_level[i + 1]).encode()
                ).hexdigest()
            else:
                # Handle odd number of transactions by duplicating the last one
                combined_hash = hashlib.sha256(
                    (current_level[i] + current_level[i]).encode()
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
